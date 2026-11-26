# 06. The order history page takes half a second (SQL on SQLite)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"My order history page is slow, and it gets slower the more orders the shop has."

## Reproduce

```bash
./run-case.sh 6
```

Uses Python's built-in `sqlite3`; nothing to install. The data is 200 customers, 20,000 orders and 100,000 order items, generated deterministically.

## Investigation

1. **Measure before guessing.** One request for one customer (100 orders) took a median of 509 ms.
2. **Count the statements.** A trace callback on the connection showed 101 `SELECT`s for one request: one for the orders and one per order for its items. That is an N+1.
3. **Hypothesis: the N+1 is the whole problem.** Tested by rewriting to a single join. Not enough on its own: the join still did a full scan (see step 4), so the single query was slow too.
4. **Read the plans** (`EXPLAIN QUERY PLAN`):
   - orders by customer: `SCAN orders` + `USE TEMP B-TREE FOR ORDER BY`
   - items by order, run 100 times: `SCAN order_items`
   Each of the 100 item lookups read all 100,000 rows. Foreign key columns are not indexed automatically.
5. **Fix both and re-read the plans.** After adding two indexes and the join:
   - `SEARCH o USING COVERING INDEX orders_by_customer (customer_id=?)`
   - `SEARCH i USING INDEX items_by_order (order_id=?)`

## Root cause

An N+1 query pattern, with each of the per-order queries scanning the whole `order_items` table because `order_id` (and `orders.customer_id`) had no index.

## Fix

`schema.sql` adds `orders(customer_id, placed_at)` and `order_items(order_id)` indexes, and `app.py` loads orders and items in one left join, so an order that has no items is still listed, as it was before the rewrite.

## Measured result

n=5 runs after one warm-up, same process, SQLite 3.46.1, Python 3.14.4, AMD Ryzen 5 PRO 5650U, with the statement-trace callback attached (it adds a little overhead to both):

| | statements | request time (ms, median of 5; range) |
|---|---|---|
| broken | 101 | 509 (433 to 779) |
| fixed | 1 | 0.6 (0.6 to 1.8) |

Your numbers will differ; the ratio and the plans are the point. The timing is shown by `./run-case.sh 6` and is not asserted by the test, because timings are flaky in CI.

## Why the regression test would have caught it

A test lists an order with no items: my first version of this fix used an inner join, which silently dropped it.

It does not time anything. It asserts the two properties that cause the slowness: one `SELECT` per request, and no `SCAN` of a table in the query plan. Those are deterministic. Deliberate break: removing only the `order_items` index (keeping the join) fails the plan check (`SCAN i`), so the test guards the index and the query shape separately.

## How to spot this class next time

- A page whose latency grows with the number of rows it shows: count the statements per request.
- Run `EXPLAIN QUERY PLAN` on every query the request runs and look for `SCAN` on a big table.
- Index foreign keys deliberately, and put the filter column first, then the sort column.

## Limits

SQLite's planner differs from PostgreSQL's (for example it can build a temporary "automatic index" for a join), so the plan text would differ there; the method carries over. The data is synthetic and uniform.

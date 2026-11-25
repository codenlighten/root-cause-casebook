import sqlite3


def orders_with_items(conn: sqlite3.Connection, customer_id: int) -> list[dict]:
    rows = conn.execute(
        """SELECT o.id, o.placed_at, i.sku, i.qty
             FROM orders o JOIN order_items i ON i.order_id = o.id
            WHERE o.customer_id = ?
            ORDER BY o.placed_at, o.id, i.id""",
        (customer_id,),
    ).fetchall()
    by_id: dict[int, dict] = {}
    for order_id, placed_at, sku, qty in rows:
        order = by_id.setdefault(order_id, {"id": order_id, "placed_at": placed_at, "items": []})
        order["items"].append((sku, qty))
    return list(by_id.values())

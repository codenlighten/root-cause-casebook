import sqlite3
import unittest

import app
import seed

CUSTOMER = 7  # owns 100 of the 20,000 orders


class OrdersWithItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")
        seed.build(cls.conn)

    def run_traced(self):
        statements = []
        self.conn.set_trace_callback(statements.append)
        result = app.orders_with_items(self.conn, CUSTOMER)
        self.conn.set_trace_callback(None)
        return result, [s for s in statements if s.lstrip().upper().startswith("SELECT")]

    def test_returns_every_order_with_its_five_items(self):
        result, _ = self.run_traced()
        self.assertEqual(len(result), 100)
        self.assertTrue(all(len(o["items"]) == 5 for o in result))

    def test_an_order_with_no_items_is_still_listed(self):
        self.addCleanup(self.conn.rollback)
        self.conn.execute("INSERT INTO orders (id, customer_id, placed_at) VALUES (900001, 900, '2026-01-01')")
        result = app.orders_with_items(self.conn, 900)
        self.assertEqual(result, [{"id": 900001, "placed_at": "2026-01-01", "items": []}])

    def test_uses_one_statement_not_one_per_order(self):
        _, selects = self.run_traced()
        self.assertEqual(len(selects), 1, f"{len(selects)} SELECTs for one request")

    def test_no_query_scans_a_whole_table(self):
        _, selects = self.run_traced()
        for sql in selects:
            plan = [row[3] for row in self.conn.execute("EXPLAIN QUERY PLAN " + sql)]
            self.assertFalse([p for p in plan if p.startswith("SCAN")], f"full scan in plan {plan} for: {sql}")


if __name__ == "__main__":
    unittest.main()

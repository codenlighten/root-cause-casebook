"""Deterministic test data: 200 customers, 20,000 orders, 100,000 order items."""
import sqlite3
from pathlib import Path


def build(conn: sqlite3.Connection) -> None:
    conn.executescript((Path(__file__).parent / "schema.sql").read_text())
    conn.executemany("INSERT INTO customers(id, name) VALUES (?, ?)",
                     [(c, f"customer {c}") for c in range(1, 201)])
    conn.executemany("INSERT INTO orders(id, customer_id, placed_at) VALUES (?, ?, ?)",
                     [(o, o % 200 + 1, f"2026-{o % 12 + 1:02d}-{o % 28 + 1:02d}") for o in range(1, 20001)])
    conn.executemany("INSERT INTO order_items(order_id, sku, qty) VALUES (?, ?, ?)",
                     [(o, f"sku-{(o * 7 + k) % 500}", k + 1) for o in range(1, 20001) for k in range(5)])
    conn.commit()

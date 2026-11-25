CREATE TABLE customers   (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders      (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, placed_at TEXT NOT NULL);
CREATE TABLE order_items (id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, sku TEXT NOT NULL, qty INTEGER NOT NULL);

-- Foreign keys are not indexed automatically. Both are looked up by these columns.
CREATE INDEX orders_by_customer ON orders (customer_id, placed_at);
CREATE INDEX items_by_order     ON order_items (order_id);

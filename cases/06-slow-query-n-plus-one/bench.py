import sqlite3
import time

import app
import seed

conn = sqlite3.connect(":memory:")
seed.build(conn)
statements = []
conn.set_trace_callback(statements.append)

timings = []
for _ in range(5):
    del statements[:]
    start = time.perf_counter()
    app.orders_with_items(conn, 7)
    timings.append((time.perf_counter() - start) * 1000)
conn.set_trace_callback(None)

print(f"statements per request: {len(statements)}")
print("request time ms, 5 runs: " + ", ".join(f"{t:.1f}" for t in timings) + f"  (median {sorted(timings)[2]:.1f})")
seen = set()
for sql in statements:
    key = sql.split("?")[0][:40] if "?" in sql else sql[:40]
    if key in seen or not sql.lstrip().upper().startswith("SELECT"):
        continue
    seen.add(key)
    print("EXPLAIN QUERY PLAN", " ".join(sql.split())[:90])
    for row in conn.execute("EXPLAIN QUERY PLAN " + sql):
        print("   ", row[3])

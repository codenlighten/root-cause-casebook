# 09. The service that grows until it is restarted (Python)

> **Constructed example.** This bug was written for this repository to demonstrate a diagnosis method. It is not a report from any client, employer or production system.

## Symptom

"Memory use climbs steadily over days and the worker is restarted every night to cope. Traffic is flat."

## Reproduce

```bash
./run-case.sh 9
```

The "extra evidence" section prints measured growth for the broken and fixed code.

## Investigation

1. **Characterise the growth.** Linear in the number of requests, not in time, and it does not drop after quiet periods. A steady climb that never falls is a leak or an unbounded structure, not fragmentation.
2. **Hypothesis: leaked file handles or sockets.** Rejected. The open-descriptor count (`/proc/self/fd`) was 4 before and 4 after 100,000 requests.
3. **Hypothesis: garbage the collector has not freed yet.** Rejected. `gc.collect()` released nothing: 125.5 MB traced before and after. The objects are still reachable.
4. **Find what holds them.** A `tracemalloc` snapshot comparison after 100,000 requests showed 100,000 live result strings of about 1 KB (101 MiB) and 100,000 key tuples allocated at the line that stores into `self._cache`. The count of live objects equals the number of distinct requests, so nothing is being released.
5. **Read the code.** `MAX_ENTRIES = 1000` is declared "intended size of the cache" and never used. Nothing is ever evicted, and queries are open-ended, so the key space is effectively unbounded.

## Root cause

The result cache had no eviction. The intended size limit existed only as an unused constant, so each new distinct key stayed in memory forever.

## Fix

An LRU: a hit moves the key to the newest end, and inserting past `MAX_ENTRIES` evicts from the oldest end.

## Measured result

100,000 lookups of distinct keys, about 1 KB per result, traced with `tracemalloc` (n=1, deterministic workload; Python 3.14.4, AMD Ryzen 5 PRO 5650U):

| lookups | broken entries | broken MB | fixed entries | fixed MB |
|---|---|---|---|---|
| 25,000 | 25,000 | 31.4 | 1,000 | 1.3 |
| 50,000 | 50,000 | 62.8 | 1,000 | 1.3 |
| 75,000 | 75,000 | 92.8 | 1,000 | 1.3 |
| 100,000 | 100,000 | 125.5 | 1,000 | 1.3 |

## Why the regression test would have caught it

It checks the cache size after 5 x the limit of distinct keys (a size check is exact, unlike a memory measurement) and that the least recently used entry is the one evicted while a recently touched one survives. Deliberate break: deleting the eviction loop fails both the size test and the LRU test (5,000 entries, not at most 1,000).

## How to spot this class next time

- Memory that rises with requests and never falls: count the entries of every long-lived dict, list and cache.
- Rule out handles (`/proc/self/fd`) and uncollected garbage (`gc.collect()`) before blaming a library.
- Every cache needs a bound and an eviction rule. A constant that is declared and not used is a smell.

## Limits

Not thread-safe (add a lock if lookups can run concurrently), and no expiry by time. In Python, `functools.lru_cache(maxsize=...)` provides the same bound for simple functions.

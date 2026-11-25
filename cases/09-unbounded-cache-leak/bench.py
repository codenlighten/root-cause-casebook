import gc
import os
import tracemalloc

from resolver import Resolver


def open_fds() -> int:
    return len(os.listdir("/proc/self/fd")) if os.path.isdir("/proc/self/fd") else -1


resolver = Resolver(lambda user, query: "x" * 1000 + f"{user}:{query}")
tracemalloc.start()
fds_before = open_fds()
print("lookups   entries  traced MB")
for i in range(1, 100_001):
    resolver.lookup(i % 5000, f"query-{i}")
    if i % 25_000 == 0:
        current, _ = tracemalloc.get_traced_memory()
        print(f"{i:>7}  {len(resolver):>8}  {current / 1e6:>9.1f}")
gc.collect()
current, _ = tracemalloc.get_traced_memory()
print(f"after gc.collect(): {current / 1e6:.1f} MB traced; open fds {fds_before} -> {open_fds()}")

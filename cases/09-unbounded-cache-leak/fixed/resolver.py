"""Caches the result of an expensive per-user lookup."""
from collections import OrderedDict
from typing import Callable


class Resolver:
    MAX_ENTRIES = 1000

    def __init__(self, fetch: Callable[[object, str], str]) -> None:
        self._fetch = fetch
        self._cache: OrderedDict[tuple[object, str], str] = OrderedDict()

    def __len__(self) -> int:
        return len(self._cache)

    def lookup(self, user: object, query: str) -> str:
        key = (user, query)
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        value = self._fetch(user, query)
        self._cache[key] = value
        while len(self._cache) > self.MAX_ENTRIES:
            self._cache.popitem(last=False)  # drop the least recently used
        return value

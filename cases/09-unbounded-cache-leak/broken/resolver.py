"""Caches the result of an expensive per-user lookup."""
from typing import Callable


class Resolver:
    MAX_ENTRIES = 1000  # intended size of the cache

    def __init__(self, fetch: Callable[[object, str], str]) -> None:
        self._fetch = fetch
        self._cache: dict[tuple[object, str], str] = {}

    def __len__(self) -> int:
        return len(self._cache)

    def lookup(self, user: object, query: str) -> str:
        key = (user, query)
        if key not in self._cache:
            self._cache[key] = self._fetch(user, query)
        return self._cache[key]

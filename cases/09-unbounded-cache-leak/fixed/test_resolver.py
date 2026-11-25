import unittest

from resolver import Resolver


class Cache(unittest.TestCase):
    def make(self):
        self.calls = []

        def fetch(user, query):
            self.calls.append((user, query))
            return f"result for {user}/{query}"

        return Resolver(fetch)

    def test_repeat_lookup_is_served_from_cache(self):
        r = self.make()
        self.assertEqual(r.lookup(1, "a"), r.lookup(1, "a"))
        self.assertEqual(self.calls, [(1, "a")])

    def test_cache_does_not_grow_past_its_limit(self):
        r = self.make()
        for i in range(5 * Resolver.MAX_ENTRIES):
            r.lookup(i, "q")
        self.assertLessEqual(len(r), Resolver.MAX_ENTRIES)

    def test_least_recently_used_entry_is_evicted_first(self):
        r = self.make()
        r.lookup("hot", "q")
        for i in range(Resolver.MAX_ENTRIES - 1):
            r.lookup(i, "q")
        r.lookup("hot", "q")          # touch it: now the newest
        r.lookup("one more", "q")     # forces one eviction
        self.calls.clear()
        r.lookup("hot", "q")
        self.assertEqual(self.calls, [], "the recently used entry was evicted")
        r.lookup(0, "q")
        self.assertEqual(self.calls, [(0, "q")], "the oldest entry should have been the one evicted")


if __name__ == "__main__":
    unittest.main()

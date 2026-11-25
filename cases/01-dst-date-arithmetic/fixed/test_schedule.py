import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from schedule import next_daily

NY = ZoneInfo("America/New_York")


class NextDaily(unittest.TestCase):
    def test_keeps_nine_oclock_across_spring_forward(self):
        # US clocks jump forward on 2026-03-08.
        self.assertEqual(next_daily(datetime(2026, 3, 7, 9, 0, tzinfo=NY)),
                         datetime(2026, 3, 8, 9, 0, tzinfo=NY))

    def test_keeps_nine_oclock_across_fall_back(self):
        # US clocks go back on 2026-11-01.
        self.assertEqual(next_daily(datetime(2026, 10, 31, 9, 0, tzinfo=NY)),
                         datetime(2026, 11, 1, 9, 0, tzinfo=NY))

    def test_ordinary_day(self):
        self.assertEqual(next_daily(datetime(2026, 6, 1, 9, 0, tzinfo=NY)),
                         datetime(2026, 6, 2, 9, 0, tzinfo=NY))


if __name__ == "__main__":
    unittest.main()

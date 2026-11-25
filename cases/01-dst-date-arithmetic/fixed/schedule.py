"""Daily reminder scheduling."""
from datetime import datetime, timedelta


def next_daily(at: datetime) -> datetime:
    """Return the next daily occurrence of a timezone-aware reminder time.

    "Every day at 09:00" is a wall-clock rule, so the day is added to the local
    wall time and the zone's UTC offset is looked up again for the result.
    """
    return at + timedelta(days=1)

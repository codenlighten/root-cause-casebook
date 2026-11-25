"""Daily reminder scheduling."""
from datetime import datetime, timedelta, timezone


def next_daily(at: datetime) -> datetime:
    """Return the next daily occurrence of a timezone-aware reminder time."""
    return (at.astimezone(timezone.utc) + timedelta(days=1)).astimezone(at.tzinfo)

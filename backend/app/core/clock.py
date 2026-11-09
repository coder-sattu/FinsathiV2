"""Injectable clock service."""

from datetime import date, datetime, timezone


class Clock:
    """Provides current date and time."""

    def __init__(self, fixed_today: date | None = None) -> None:
        # set fixed date
        self._fixed_today = fixed_today

    def today(self) -> date:
        # return date
        if self._fixed_today:
            return self._fixed_today
        return datetime.now(timezone.utc).date()

    def now(self) -> datetime:
        # return datetime
        return datetime.now(timezone.utc)

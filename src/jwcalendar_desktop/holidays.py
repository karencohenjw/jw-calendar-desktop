"""United States federal holiday dates and weekend observance."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Holiday:
    name: str
    statutory_date: date
    observed_date: date

    def as_json(self) -> dict[str, str]:
        return {"name": self.name, "statutoryDate": self.statutory_date.isoformat(),
                "observedDate": self.observed_date.isoformat()}


def _observed(day: date) -> date:
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


def federal_holidays(year: int) -> list[Holiday]:
    """Return nationwide US federal holidays under 5 USC 6103.

    This models the standard Monday-Friday federal work schedule. It excludes
    one-off presidential closures, inauguration day, and state/local holidays.
    """
    if not 1 <= year <= 9999:
        raise ValueError("Year must be between 1 and 9999.")

    def nth_weekday(month: int, weekday: int, occurrence: int) -> date:
        first = date(year, month, 1)
        return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (occurrence - 1))

    def last_weekday(month: int, weekday: int) -> date:
        last = date(year, month, calendar.monthrange(year, month)[1])
        return last - timedelta(days=(last.weekday() - weekday) % 7)

    statutory = [
        ("New Year's Day", date(year, 1, 1)),
        ("Birthday of Martin Luther King, Jr.", nth_weekday(1, 0, 3)),
        ("Washington's Birthday", nth_weekday(2, 0, 3)),
        ("Memorial Day", last_weekday(5, 0)),
        ("Juneteenth National Independence Day", date(year, 6, 19)),
        ("Independence Day", date(year, 7, 4)),
        ("Labor Day", nth_weekday(9, 0, 1)),
        ("Columbus Day", nth_weekday(10, 0, 2)),
        ("Veterans Day", date(year, 11, 11)),
        ("Thanksgiving Day", nth_weekday(11, 3, 4)),
        ("Christmas Day", date(year, 12, 25)),
    ]
    return [Holiday(name, day, _observed(day)) for name, day in statutory]

"""Offline calendar presentation and export helpers.

Calendar arithmetic is delegated to the upstream jwcalendar-calendrical
library. This module adapts its immutable date models into UI-friendly rows.
"""

from __future__ import annotations

import calendar
import csv
import html
import io
import locale
import re
from dataclasses import dataclass
from typing import Literal

from jwcalendar_calendrical import (
    CivilDate,
    JulianDate,
    MONDAY_FIRST,
    SUNDAY_FIRST,
    WeekModel,
    build_month,
    days_in_month,
    gregorian_to_fixed,
    gregorian_to_julian_calendar,
    is_leap_year,
    julian_calendar_to_gregorian,
    to_iso_week_date,
)
from jwcalendar_calendrical.systems.julian import (
    fixed_to_julian,
    julian_days_in_month,
    julian_to_fixed,
)

CalendarKind = Literal["gregorian", "julian"]
WeekStart = Literal["monday", "sunday"]


@dataclass(frozen=True)
class CalendarCell:
    date: CivilDate | JulianDate | None
    in_month: bool
    iso_week: str | None = None


def parse_date(value: str, kind: CalendarKind = "gregorian") -> CivilDate | JulianDate:
    """Parse a strict positive-year ISO date under the selected calendar."""
    value = value.strip()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Enter a date in YYYY-MM-DD format.")
    pieces = value.split("-")
    year, month, day = map(int, pieces)
    if not 1 <= year <= 9999:
        raise ValueError("Supported years are 1 through 9999.")
    if kind == "gregorian":
        return CivilDate(year, month, day)
    if kind == "julian":
        return JulianDate(year, month, day)
    raise ValueError("Choose Gregorian or Julian calendar.")


def date_to_fixed(value: CivilDate | JulianDate) -> int:
    if isinstance(value, CivilDate):
        return gregorian_to_fixed(value)
    return julian_to_fixed(value)


def iso_date(value: CivilDate | JulianDate) -> str:
    return f"{value.year:04d}-{value.month:02d}-{value.day:02d}"


def date_details(value: CivilDate | JulianDate) -> dict[str, str]:
    """Return weekday, ordinal, cross-calendar date, ISO week and JDN."""
    fixed = date_to_fixed(value)
    weekday = calendar.day_name[(fixed - 1) % 7]
    ordinal = value.day
    month_lengths = (
        [days_in_month(value.year, month) for month in range(1, value.month)]
        if isinstance(value, CivilDate)
        else [julian_days_in_month(value.year, month) for month in range(1, value.month)]
    )
    ordinal += sum(month_lengths)
    if isinstance(value, CivilDate):
        gregorian = value
        julian = gregorian_to_julian_calendar(value)
    else:
        julian = value
        try:
            gregorian = julian_calendar_to_gregorian(value)
        except ValueError:
            gregorian = None
    if gregorian is None:
        iso_week = "Unavailable outside the supported Gregorian range"
        gregorian_text = "Outside the supported Gregorian range"
    else:
        iso_year, iso_week_number, iso_weekday = to_iso_week_date(gregorian)
        iso_week = f"{iso_year:04d}-W{iso_week_number:02d}-{iso_weekday}"
        gregorian_text = iso_date(gregorian)
    jdn = int(fixed + 1721425)
    return {
        "date": iso_date(value),
        "calendar": "Gregorian" if isinstance(value, CivilDate) else "Julian",
        "weekday": weekday,
        "ordinal": f"{ordinal} of {value.year}",
        "gregorian": gregorian_text,
        "julian": iso_date(julian),
        "iso_week": iso_week,
        "jdn": str(jdn),
        "leap_year": str(
            is_leap_year(value.year)
            if isinstance(value, CivilDate)
            else value.year % 4 == 0
        ),
    }


def _week_model(first_weekday: WeekStart) -> WeekModel:
    if first_weekday == "monday":
        return MONDAY_FIRST
    if first_weekday == "sunday":
        return SUNDAY_FIRST
    raise ValueError("Week start must be Monday or Sunday.")


def month_cells(
    year: int,
    month: int,
    *,
    kind: CalendarKind = "gregorian",
    week_start: WeekStart = "sunday",
) -> list[list[CalendarCell]]:
    """Build a natural-height month grid with ISO week labels."""
    if not 1 <= year <= 9999 or not 1 <= month <= 12:
        raise ValueError("Year must be 1..9999 and month must be 1..12.")
    model = _week_model(week_start)
    rows: list[list[CalendarCell]] = []
    if kind == "gregorian":
        grid = build_month(year, month, week_model=model, adjacent_days=True)
        for row in grid.rows:
            cells = [CalendarCell(cell.date, cell.in_month) for cell in row]
            iso_week = _iso_week_for_row(cells, week_start)
            rows.append([CalendarCell(c.date, c.in_month, iso_week) for c in cells])
        return rows
    if kind != "julian":
        raise ValueError("Choose Gregorian or Julian calendar.")

    first = JulianDate(year, month, 1)
    length = julian_days_in_month(year, month)
    leading = ((julian_to_fixed(first) - 1) % 7 - model.first_weekday) % 7
    row_count = (leading + length + 6) // 7
    start_fixed = julian_to_fixed(first) - leading
    for row_index in range(row_count):
        cells: list[CalendarCell] = []
        for col in range(7):
            fixed = start_fixed + row_index * 7 + col
            try:
                date = fixed_to_julian(fixed)
            except ValueError:
                date = None
            cells.append(
                CalendarCell(
                    date=date,
                    in_month=bool(date and date.year == year and date.month == month),
                )
            )
        iso_week = _iso_week_for_row(cells, week_start)
        rows.append([CalendarCell(c.date, c.in_month, iso_week) for c in cells])
    return rows


def _iso_week_for_row(cells: list[CalendarCell], week_start: WeekStart) -> str | None:
    thursday_col = 3 if week_start == "monday" else 4
    date = cells[thursday_col].date
    if date is None:
        date = next((c.date for c in cells if c.date is not None and c.in_month), None)
    if date is None:
        return None
    try:
        gregorian = date if isinstance(date, CivilDate) else julian_calendar_to_gregorian(date)
        year, week, _ = to_iso_week_date(gregorian)
    except ValueError:
        # The engine's Gregorian model begins at AD 1; the first Julian
        # calendar days predate that shared supported range.
        return None
    return f"{year:04d}-W{week:02d}"


def month_csv(year: int, month: int, *, kind: CalendarKind, week_start: WeekStart) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["week", "weekday", "date", "calendar", "in_month", "iso_week"])
    weekdays = list(calendar.day_abbr)
    first = 0 if week_start == "monday" else 6
    weekdays = weekdays[first:] + weekdays[:first]
    for row in month_cells(year, month, kind=kind, week_start=week_start):
        iso_week = next((c.iso_week for c in row if c.iso_week), "")
        for weekday, cell in zip(weekdays, row, strict=True):
            writer.writerow([
                iso_week,
                weekday,
                iso_date(cell.date) if cell.date else "",
                kind.capitalize(),
                "true" if cell.in_month else "false",
                iso_week,
            ])
    return output.getvalue()


def month_html(year: int, month: int, *, kind: CalendarKind, week_start: WeekStart) -> str:
    """Create a standalone print-ready HTML calendar without remote resources."""
    cells = month_cells(year, month, kind=kind, week_start=week_start)
    first = 0 if week_start == "monday" else 6
    weekdays = list(calendar.day_name)
    weekdays = weekdays[first:] + weekdays[:first]
    headings = "".join(f"<th scope=\"col\">{html.escape(day[:3])}</th>" for day in weekdays)
    body = []
    for row in cells:
        tds = []
        for cell in row:
            if cell.date is None:
                tds.append("<td></td>")
            else:
                css = "in-month" if cell.in_month else "adjacent"
                tds.append(f"<td class=\"{css}\">{cell.date.day}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    title = f"{calendar.month_name[month]} {year} — {kind.capitalize()} calendar"
    language = locale.getlocale(locale.LC_TIME)[0]
    language_tag = language.replace("_", "-") if language else "en"
    return f"""<!doctype html>
<html lang="{html.escape(language_tag)}"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{html.escape(title)}</title>
<style>
body{{font:16px system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#17243a}}
h1{{color:#174b9b}}table{{border-collapse:collapse;width:100%;table-layout:fixed}}
th,td{{border:1px solid #b9cbe0;text-align:center;padding:.8rem .3rem;height:3rem}}
th{{background:#e8f2ff}}td.adjacent{{color:#7c899a;background:#f6f8fb}}
@media print{{body{{max-width:none;margin:0;padding:0}}th,td{{break-inside:avoid}}}}
</style>
<h1>{html.escape(title)}</h1>
<table><thead><tr>{headings}</tr></thead><tbody>{''.join(body)}</tbody></table>
<p>Generated offline by JW Calendar.</p></html>"""


def days_between_dates(start: str, end: str, *, kind: CalendarKind = "gregorian") -> int:
    return date_to_fixed(parse_date(end, kind)) - date_to_fixed(parse_date(start, kind))

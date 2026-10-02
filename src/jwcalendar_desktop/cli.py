"""Command-line interface for JW Calendar."""

from __future__ import annotations

import argparse
import calendar
import json
import re
import sys
from datetime import date
from typing import Sequence

from . import __version__
from .core import (CalendarKind, WeekStart, date_details, days_between_dates,
                   iso_date, month_cells, month_csv, month_html, parse_date)
from .holidays import federal_holidays


def _json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _kind(value: str) -> CalendarKind:
    normalized = value.lower()
    if normalized not in {"gregorian", "julian"}:
        raise argparse.ArgumentTypeError("choose gregorian or julian")
    return normalized  # type: ignore[return-value]


def _week_start(value: str) -> WeekStart:
    normalized = value.lower()
    if normalized not in {"sunday", "monday"}:
        raise argparse.ArgumentTypeError("choose sunday or monday")
    return normalized  # type: ignore[return-value]


def _month_json(year: int, month: int, kind: CalendarKind, start: WeekStart) -> list[list[dict[str, object]]]:
    return [[{"date": iso_date(c.date) if c.date else None,
              "day": c.date.day if c.date else None,
              "inMonth": c.in_month, "isoWeek": c.iso_week} for c in row]
            for row in month_cells(year, month, kind=kind, week_start=start)]


def _structured_details(value: str, kind: CalendarKind) -> dict[str, object]:
    details = date_details(parse_date(value, kind))
    day_of_year = int(details["ordinal"].split()[0])
    days_in_year = 366 if details["leap_year"] == "True" else 365
    week_match = re.fullmatch(r"(\d{4})-W(\d{2})-(\d)", details["iso_week"])
    return {
        "date": details["date"],
        "calendar": details["calendar"].lower(),
        "weekday": details["weekday"],
        "dayOfYear": day_of_year,
        "daysInYear": days_in_year,
        "daysRemaining": days_in_year - day_of_year,
        "gregorian": details["gregorian"],
        "julian": details["julian"],
        "isoWeek": details["iso_week"],
        "isoWeekYear": int(week_match.group(1)) if week_match else None,
        "isoWeekNumber": int(week_match.group(2)) if week_match else None,
        "isoWeekday": int(week_match.group(3)) if week_match else None,
        "julianDayNumber": int(details["jdn"]),
        "isLeapYear": details["leap_year"] == "True",
    }


def _print_month(year: int, month: int, kind: CalendarKind, start: WeekStart) -> None:
    rows = month_cells(year, month, kind=kind, week_start=start)
    offset = 0 if start == "monday" else 6
    weekdays = list(calendar.day_abbr)
    weekdays = weekdays[offset:] + weekdays[:offset]
    print(f"{calendar.month_name[month]} {year} — {kind.title()} calendar")
    print(f"{'ISO week':>9}  " + " ".join(f"{d:>3}" for d in weekdays))
    for row in rows:
        week = next((c.iso_week for c in row if c.iso_week), "—")
        days = []
        for cell in row:
            label = f"{cell.date.day:2}" if cell.date else "  "
            if cell.date and not cell.in_month:
                label = f"({cell.date.day:2})"
            days.append(f"{label:>4}")
        print(f"{week:>9}  " + " ".join(days))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jwcalendar",
        description="Browse and calculate Gregorian and Julian dates offline.")
    parser.add_argument("--version", action="version", version=f"jwcalendar {__version__}")
    sub = parser.add_subparsers(dest="command")
    month = sub.add_parser("month", help="show a month grid")
    month.add_argument("date", nargs="?", help="YYYY-MM; defaults to the current month")
    month.add_argument("--calendar", type=_kind, default="gregorian")
    month.add_argument("--week-start", type=_week_start, default="sunday")
    month.add_argument("--json", action="store_true", help="emit JSON")
    month.add_argument("--csv", action="store_true", help="emit CSV")
    month.add_argument("--html", action="store_true", help="emit print-ready HTML")
    year = sub.add_parser("year", help="show all months of a year")
    year.add_argument("year", nargs="?", type=int, default=date.today().year)
    year.add_argument("--calendar", type=_kind, default="gregorian")
    year.add_argument("--week-start", type=_week_start, default="sunday")
    year.add_argument("--json", action="store_true")
    details = sub.add_parser("date", help="inspect a date")
    details.add_argument("date", help="YYYY-MM-DD")
    details.add_argument("--calendar", type=_kind, default="gregorian")
    details.add_argument("--json", action="store_true")
    convert = sub.add_parser("convert", help="show Gregorian and Julian equivalents")
    convert.add_argument("date", help="YYYY-MM-DD")
    convert.add_argument("--from", dest="calendar", type=_kind, default="gregorian")
    convert.add_argument("--json", action="store_true")
    diff = sub.add_parser("difference", help="count signed elapsed civil days")
    diff.add_argument("start", help="YYYY-MM-DD")
    diff.add_argument("end", help="YYYY-MM-DD")
    diff.add_argument("--calendar", type=_kind, default="gregorian")
    diff.add_argument("--json", action="store_true")
    holidays = sub.add_parser("holidays", help="list US federal holidays and observed dates")
    holidays.add_argument("year", nargs="?", type=int, default=date.today().year)
    holidays.add_argument("--json", action="store_true")
    return parser


def _month_args(value: str | None, kind: CalendarKind) -> tuple[int, int]:
    value = value or date.today().strftime("%Y-%m")
    try:
        if len(value) == 7 and value[4] == "-":
            year, month = map(int, value.split("-"))
            if 1 <= year <= 9999 and 1 <= month <= 12:
                return year, month
        else:
            parsed = parse_date(value, kind)
            return parsed.year, parsed.month
    except ValueError:
        pass
    raise ValueError("Month must be YYYY-MM (year 1..9999).")


def run(args: argparse.Namespace) -> int:
    if args.command is None:
        _print_month(date.today().year, date.today().month, "gregorian", "sunday")
    elif args.command == "month":
        year, month = _month_args(args.date, args.calendar)
        if args.csv:
            print(month_csv(year, month, kind=args.calendar, week_start=args.week_start), end="")
        elif args.html:
            print(month_html(year, month, kind=args.calendar, week_start=args.week_start))
        elif args.json:
            _json({"year": year, "month": month, "calendar": args.calendar,
                   "weekStart": args.week_start,
                   "weeks": _month_json(year, month, args.calendar, args.week_start)})
        else:
            _print_month(year, month, args.calendar, args.week_start)
    elif args.command == "year":
        if not 1 <= args.year <= 9999:
            raise ValueError("Year must be between 1 and 9999.")
        if args.json:
            _json({"year": args.year, "calendar": args.calendar,
                   "months": [{"month": m, "weeks": _month_json(args.year, m, args.calendar, args.week_start)}
                              for m in range(1, 13)]})
        else:
            for month in range(1, 13):
                _print_month(args.year, month, args.calendar, args.week_start)
                if month != 12:
                    print()
    elif args.command in {"date", "convert"}:
        details = _structured_details(args.date, args.calendar)
        if args.json:
            _json(details)
        elif args.command == "convert":
            print(f"Gregorian: {details['gregorian']}\nJulian: {details['julian']}\nJulian Day Number: {details['julianDayNumber']}")
        else:
            print(f"Date: {details['date']} ({details['calendar']})")
            print(f"Weekday: {details['weekday']}")
            print(f"Day of year: {details['dayOfYear']} of {details['daysInYear']}")
            print(f"Gregorian: {details['gregorian']}\nJulian: {details['julian']}")
            print(f"ISO week: {details['isoWeek']}\nJulian Day Number: {details['julianDayNumber']}")
            print(f"Leap year: {'Yes' if details['isLeapYear'] else 'No'}")
    elif args.command == "difference":
        count = days_between_dates(args.start, args.end, kind=args.calendar)
        _json({"start": args.start, "end": args.end, "calendar": args.calendar,
               "elapsedDays": count}) if args.json else print(f"{count} elapsed civil days")
    elif args.command == "holidays":
        entries = [h.as_json() for h in federal_holidays(args.year)]
        if args.json:
            _json({"jurisdiction": "United States federal", "year": args.year,
                   "holidays": entries})
        else:
            print(f"United States federal holidays — {args.year}")
            for item in entries:
                observed = f" (observed {item['observedDate']})" if item["observedDate"] != item["statutoryDate"] else ""
                print(f"{item['statutoryDate']}  {item['name']}{observed}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except ValueError as error:
        print(f"jwcalendar: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

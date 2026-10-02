import unittest

from jwcalendar_desktop.core import (
    date_details,
    days_between_dates,
    month_cells,
    month_csv,
    month_html,
    parse_date,
)
from jwcalendar_calendrical import CivilDate, JulianDate


class DateParsingTests(unittest.TestCase):
    def test_parses_both_calendar_models(self):
        self.assertEqual(parse_date("2000-02-29"), CivilDate(2000, 2, 29))
        self.assertEqual(parse_date("1900-02-29", "julian"), JulianDate(1900, 2, 29))

    def test_rejects_bad_format_and_invalid_dates(self):
        for value in ("2000-2-09", "2000/02/09", "0-01-01", "10000-01-01", "٢٠٠٠-٠١-٠١"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_date(value)
        for value in ("1900-02-29", "2000-13-01", "2000-04-31"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_date(value)

    def test_rejects_unknown_calendar(self):
        with self.assertRaises(ValueError):
            parse_date("2024-01-01", "reform")


class CalendarArithmeticTests(unittest.TestCase):
    def test_gregorian_leap_year_rules(self):
        expected = {1900: False, 2000: True, 2024: True, 2027: False, 2028: True, 2100: False}
        for year, leap in expected.items():
            with self.subTest(year=year):
                value = date_details(parse_date(f"{year:04d}-12-31"))
                self.assertEqual(value["leap_year"], str(leap))
                self.assertEqual(value["ordinal"], f"{366 if leap else 365} of {year}")

    def test_requested_year_boundaries_and_iso_weeks(self):
        expected = {
            "2026-12-31": "2026-W53-4",
            "2027-01-01": "2026-W53-5",
            "2027-12-31": "2027-W52-5",
            "2028-01-01": "2027-W52-6",
            "2028-02-29": "2028-W09-2",
        }
        for value, iso_week in expected.items():
            with self.subTest(value=value):
                self.assertEqual(date_details(parse_date(value))["iso_week"], iso_week)

    def test_gregorian_julian_round_trip_for_supported_dates(self):
        from jwcalendar_calendrical import gregorian_to_julian_calendar, julian_calendar_to_gregorian

        for value in ("0001-01-01", "1582-10-14", "1900-03-01", "2000-02-29", "2028-02-29", "9999-12-31"):
            with self.subTest(value=value):
                original = parse_date(value)
                self.assertEqual(julian_calendar_to_gregorian(gregorian_to_julian_calendar(original)), original)

    def test_gregorian_leap_centuries_and_ordinal(self):
        self.assertEqual(date_details(parse_date("2000-02-29"))["leap_year"], "True")
        self.assertEqual(date_details(parse_date("1900-03-01"))["leap_year"], "False")
        self.assertEqual(date_details(parse_date("2000-12-31"))["ordinal"], "366 of 2000")
        self.assertEqual(date_details(parse_date("1900-12-31"))["ordinal"], "365 of 1900")

    def test_julian_leap_year_uses_every_fourth_year(self):
        self.assertEqual(date_details(parse_date("1900-02-29", "julian"))["leap_year"], "True")

    def test_julian_year_one_dates_have_safe_details(self):
        details = date_details(parse_date("0001-01-01", "julian"))
        self.assertEqual(details["julian"], "0001-01-01")
        self.assertEqual(details["gregorian"], "Outside the supported Gregorian range")
        self.assertTrue(details["jdn"].isdigit())

    def test_julian_gregorian_reform_boundary_same_absolute_day(self):
        julian = date_details(parse_date("1582-10-04", "julian"))
        gregorian = date_details(parse_date("1582-10-14", "gregorian"))
        self.assertEqual(julian["gregorian"], "1582-10-14")
        self.assertEqual(gregorian["julian"], "1582-10-04")
        self.assertEqual(julian["jdn"], gregorian["jdn"])
        self.assertEqual(days_between_dates("1582-10-04", "1582-10-14", kind="gregorian"), 10)

    def test_jdn_and_week_year_boundary(self):
        new_year = date_details(parse_date("2000-01-01"))
        self.assertEqual(new_year["jdn"], "2451545")
        self.assertEqual(new_year["iso_week"], "1999-W52-6")
        self.assertEqual(date_details(parse_date("2021-01-01"))["iso_week"], "2020-W53-5")

    def test_difference_is_signed_and_elapsed(self):
        self.assertEqual(days_between_dates("2024-12-31", "2025-01-01"), 1)
        self.assertEqual(days_between_dates("2025-01-01", "2024-12-31"), -1)
        self.assertEqual(days_between_dates("2024-02-28", "2024-03-01"), 2)

    def test_invalid_date_difference_is_reported(self):
        with self.assertRaises(ValueError):
            days_between_dates("2024-02-30", "2024-03-01")


class CalendarGridTests(unittest.TestCase):
    def test_month_rows_cover_all_days_and_respect_week_start(self):
        sunday = month_cells(2021, 1, week_start="sunday")
        monday = month_cells(2021, 1, week_start="monday")
        self.assertEqual(len(sunday), 6)
        self.assertEqual(len(monday), 5)
        for rows in (sunday, monday):
            self.assertTrue(all(len(row) == 7 for row in rows))
            in_month = [cell.date.day for row in rows for cell in row if cell.in_month]
            self.assertEqual(in_month, list(range(1, 32)))

    def test_julian_grid_and_early_year_edge(self):
        rows = month_cells(1900, 2, kind="julian", week_start="monday")
        dates = [cell.date.day for row in rows for cell in row if cell.in_month]
        self.assertEqual(dates, list(range(1, 30)))
        early_year = month_cells(1, 1, kind="julian")
        self.assertTrue(all(len(row) == 7 for row in early_year))

    def test_month_arguments_are_validated(self):
        for year, month in ((0, 1), (10000, 1), (2024, 0), (2024, 13)):
            with self.subTest(year=year, month=month), self.assertRaises(ValueError):
                month_cells(year, month)
        with self.assertRaises(ValueError):
            month_cells(2024, 1, week_start="friday")

    def test_export_content_is_self_contained(self):
        html = month_html(2024, 2, kind="gregorian", week_start="monday")
        csv = month_csv(2024, 2, kind="gregorian", week_start="monday")
        self.assertIn("February 2024", html)
        self.assertIn("Generated offline", html)
        self.assertNotIn("https://", html)
        self.assertIn("week,weekday,date,calendar,in_month,iso_week", csv)
        self.assertIn("2024-02-29", csv)


if __name__ == "__main__":
    unittest.main()

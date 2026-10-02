import json
import os
import subprocess
import sys
import unittest

from jwcalendar_desktop.cli import main


class CommandLineTests(unittest.TestCase):
    def invoke(self, *args):
        from contextlib import redirect_stdout
        from io import StringIO

        output = StringIO()
        with redirect_stdout(output):
            code = main(list(args))
        return code, output.getvalue()

    def test_date_json_contains_typed_calendar_fields(self):
        code, output = self.invoke("date", "2028-02-29", "--json")
        record = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(record["dayOfYear"], 60)
        self.assertEqual(record["daysInYear"], 366)
        self.assertEqual(record["daysRemaining"], 306)
        self.assertEqual(record["isoWeekYear"], 2028)
        self.assertIs(record["isLeapYear"], True)

    def test_month_and_export_formats(self):
        code, output = self.invoke("month", "2027-01", "--week-start", "monday", "--json")
        result = json.loads(output)
        self.assertEqual(code, 0)
        self.assertEqual(result["weekStart"], "monday")
        self.assertEqual(len(result["weeks"][0]), 7)
        code, output = self.invoke("month", "2028-02", "--csv")
        self.assertEqual(code, 0)
        self.assertIn("2028-02-29", output)
        code, output = self.invoke("month", "2024-02", "--html")
        self.assertEqual(code, 0)
        self.assertIn("<!doctype html>", output)
        self.assertNotIn("https://", output)

    def test_conversions_and_difference(self):
        code, output = self.invoke("convert", "1582-10-04", "--from", "julian", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["gregorian"], "1582-10-14")
        code, output = self.invoke("difference", "2024-12-31", "2025-01-01", "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["elapsedDays"], 1)

    def test_invalid_date_returns_error_status(self):
        from contextlib import redirect_stderr
        from io import StringIO

        error = StringIO()
        with redirect_stderr(error):
            code = main(["date", "2027-02-29"])
        self.assertEqual(code, 2)
        self.assertIn("valid", error.getvalue())

    def test_explicit_date_results_do_not_depend_on_timezone(self):
        results = []
        for zone in ("UTC", "America/Los_Angeles", "Asia/Tokyo"):
            environment = os.environ.copy()
            environment["TZ"] = zone
            result = subprocess.run(
                [sys.executable, "-m", "jwcalendar_desktop", "date", "2028-02-29", "--json"],
                check=True, capture_output=True, text=True, env=environment,
            )
            results.append(json.loads(result.stdout))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])


if __name__ == "__main__":
    unittest.main()

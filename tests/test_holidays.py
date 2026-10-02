import unittest

from jwcalendar_desktop.holidays import federal_holidays


class FederalHolidayTests(unittest.TestCase):
    def test_2027_statutory_and_observed_dates(self):
        entries = {holiday.name: holiday for holiday in federal_holidays(2027)}
        self.assertEqual(len(entries), 11)
        self.assertEqual(entries["Juneteenth National Independence Day"].statutory_date.isoformat(), "2027-06-19")
        self.assertEqual(entries["Juneteenth National Independence Day"].observed_date.isoformat(), "2027-06-18")
        self.assertEqual(entries["Independence Day"].statutory_date.isoformat(), "2027-07-04")
        self.assertEqual(entries["Independence Day"].observed_date.isoformat(), "2027-07-05")
        self.assertEqual(entries["Christmas Day"].observed_date.isoformat(), "2027-12-24")

    def test_fixed_holidays_observed_on_friday_and_monday(self):
        by_name = {h.name: h for h in federal_holidays(2021)}
        self.assertEqual(by_name["New Year's Day"].observed_date.isoformat(), "2021-01-01")
        self.assertEqual(by_name["Juneteenth National Independence Day"].observed_date.isoformat(), "2021-06-18")
        self.assertEqual(by_name["Independence Day"].observed_date.isoformat(), "2021-07-05")

    def test_rejects_unsupported_year(self):
        for year in (0, 10000):
            with self.subTest(year=year), self.assertRaises(ValueError):
                federal_holidays(year)


if __name__ == "__main__":
    unittest.main()

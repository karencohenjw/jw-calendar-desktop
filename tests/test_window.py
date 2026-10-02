import importlib.util
import os
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory


HAS_GI = importlib.util.find_spec("gi") is not None
HAS_DISPLAY = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


@unittest.skipUnless(HAS_GI and HAS_DISPLAY, "GTK display is not available")
class WindowSmokeTests(unittest.TestCase):
    def test_export_writes_through_gio_to_the_selected_file(self):
        import gi

        gi.require_version("Adw", "1")
        gi.require_version("Gtk", "4.0")
        from gi.repository import Adw, Gio, GLib

        from jwcalendar_desktop.window import CalendarWindow

        app = Adw.Application(
            application_id="com.jwcalendar.JWCalendar.ExportTest",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.assertTrue(app.register(None))
        window = CalendarWindow(app, "test")
        with TemporaryDirectory() as directory:
            path = Path(directory, "calendar.csv")
            loop = GLib.MainLoop()
            errors = []
            window._write_export(
                Gio.File.new_for_path(str(path)),
                "date,weekday\n2027-01-01,Fri\n",
                lambda error: (errors.append(error), loop.quit()),
            )
            GLib.timeout_add_seconds(5, loop.quit)
            loop.run()
            self.assertEqual(errors, [None])
            self.assertEqual(path.read_text(encoding="utf-8"), "date,weekday\n2027-01-01,Fri\n")
        window.destroy()
        app.quit()

    def test_window_constructs_with_native_calendar_pages(self):
        import gi

        gi.require_version("Adw", "1")
        gi.require_version("Gtk", "4.0")
        from gi.repository import Adw, Gio

        from jwcalendar_desktop.window import CalendarWindow
        from jwcalendar_calendrical import CivilDate

        app = Adw.Application(
            application_id="com.jwcalendar.JWCalendar.Test",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.assertTrue(app.register(None))
        window = CalendarWindow(app, "test")
        self.assertEqual(window.get_title(), "JW Calendar")
        self.assertEqual(window.stack.get_pages().get_n_items(), 4)
        self.assertEqual(window.stack.get_pages().get_item(0).get_icon_name(), "x-office-calendar-symbolic")
        self.assertEqual(window.stack.get_pages().get_item(1).get_icon_name(), "view-grid-symbolic")
        self.assertEqual(window.stack.get_pages().get_item(2).get_icon_name(), "accessories-calculator-symbolic")
        self.assertEqual(window.stack.get_pages().get_item(3).get_icon_name(), "help-about-symbolic")
        today = date.today()
        self.assertEqual(window._month, today.month)
        window._shift_month(1)
        self.assertEqual(window._month, (today.month % 12) + 1)
        self.assertEqual(window._year, today.year + (1 if today.month == 12 else 0))
        window._year_spin.set_value(window._year + 1)
        self.assertEqual(window._year, today.year + (1 if today.month == 12 else 0) + 1)
        window._month_spin.set_value(2028)
        window._month_dropdown.set_selected(1)
        window._select_date(None, CivilDate(2028, 2, 29))
        self.assertEqual(window._selected_date, "2028-02-29")
        selected_button = window._calendar_grid.get_first_child()
        while selected_button is not None:
            if selected_button.get_tooltip_text() == "2028-02-29 · 2028-W09":
                break
            selected_button = selected_button.get_next_sibling()
        self.assertIsNotNone(selected_button)
        self.assertTrue(selected_button.has_css_class("suggested-action"))
        self.assertFalse(selected_button.has_css_class("flat"))
        window.destroy()
        app.quit()

    def test_copy_uses_the_gtk_clipboard(self):
        import gi

        gi.require_version("Adw", "1")
        gi.require_version("Gtk", "4.0")
        from gi.repository import Adw, Gio, GLib, Gdk

        from jwcalendar_desktop.window import CalendarWindow

        app = Adw.Application(
            application_id="com.jwcalendar.JWCalendar.ClipboardTest",
            flags=Gio.ApplicationFlags.NON_UNIQUE,
        )
        self.assertTrue(app.register(None))
        window = CalendarWindow(app, "test")
        window._selected_date = "2027-01-01"
        window._copy_date()
        clipboard = Gdk.Display.get_default().get_clipboard()
        loop = GLib.MainLoop()
        result = {"text": None, "error": None}

        def copied(source, async_result, _data):
            try:
                result["text"] = source.read_text_finish(async_result)
            except Exception as error:
                result["error"] = error
            loop.quit()

        clipboard.read_text_async(None, copied, None)
        GLib.timeout_add_seconds(5, loop.quit)
        loop.run()
        self.assertIsNone(result["error"])
        self.assertEqual(result["text"], "2027-01-01")
        window.destroy()
        app.quit()


if __name__ == "__main__":
    unittest.main()

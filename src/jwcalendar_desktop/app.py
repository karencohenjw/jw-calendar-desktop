"""GTK application entry point."""

from __future__ import annotations

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gio

from . import __version__
from .window import CalendarWindow

APP_ID = "com.jwcalendar.JWCalendar"


class JWCalendarApplication(Adw.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.set_resource_base_path("/com/jwcalendar/JWCalendar")

    def do_activate(self) -> None:
        window = self.props.active_window
        if window is None:
            window = CalendarWindow(self, __version__)
        window.present()


def main() -> int:
    return JWCalendarApplication().run(None)


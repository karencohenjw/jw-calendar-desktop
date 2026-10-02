"""Libadwaita desktop interface for the offline calendar engine."""

from __future__ import annotations

import calendar
import locale
from datetime import date

import gi

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from .core import (
    CalendarKind,
    WeekStart,
    date_details,
    days_between_dates,
    iso_date,
    month_cells,
    month_csv,
    month_html,
    parse_date,
)


class CalendarWindow(Adw.ApplicationWindow):
    def __init__(self, application: Adw.Application, version: str) -> None:
        super().__init__(application=application, title="JW Calendar")
        self.set_default_size(1024, 760)
        self.set_size_request(600, 460)
        self._version = version
        today = date.today()
        self._year = today.year
        self._month = today.month
        self._kind: CalendarKind = "gregorian"
        self._week_start: WeekStart = "sunday"
        self._selected_date = today.isoformat()
        self._syncing_controls = False
        self._calendar_grid: Gtk.Grid
        self._year_grid: Gtk.Grid
        self._detail_label: Gtk.Label
        self._converter_result: Gtk.Label
        self._difference_result: Gtk.Label
        self._month_spin: Gtk.SpinButton
        self._year_spin: Gtk.SpinButton
        self._month_dropdown: Gtk.DropDown
        self._month_kind: Gtk.DropDown
        self._year_kind: Gtk.DropDown
        self._week_dropdown: Gtk.DropDown
        self._converter_kind: Gtk.DropDown
        self._difference_kind: Gtk.DropDown
        self._converter_entry: Gtk.Entry
        self._difference_start: Gtk.Entry
        self._difference_end: Gtk.Entry

        try:
            locale.setlocale(locale.LC_TIME, "")
        except locale.Error:
            pass
        self._month_names = [calendar.month_name[month] for month in range(1, 13)]
        self._weekdays = list(calendar.day_abbr)

        self._build_ui()
        self._render_month()
        self._render_year()
        self._render_details()
        keys = Gtk.EventControllerKey()
        keys.connect("key-pressed", self._on_key_pressed)
        self.add_controller(keys)

    def _build_ui(self) -> None:
        toolbar = Adw.ToolbarView()
        header = Adw.HeaderBar()
        header.set_title_widget(Adw.ViewSwitcher())
        self.switcher = header.get_title_widget()
        self.stack = Adw.ViewStack()
        self.switcher.set_stack(self.stack)
        toolbar.add_top_bar(header)

        copy_button = Gtk.Button(icon_name="edit-copy-symbolic", tooltip_text="Copy selected date")
        self._accessible_name(copy_button, "Copy selected date")
        copy_button.connect("clicked", self._copy_date)
        header.pack_start(copy_button)
        export_button = Gtk.MenuButton(icon_name="document-save-symbolic", tooltip_text="Export")
        self._accessible_name(export_button, "Export calendar")
        export_menu = Gio.Menu()
        export_menu.append("Print-ready HTML…", "win.export-html")
        export_menu.append("Calendar CSV…", "win.export-csv")
        export_button.set_menu_model(export_menu)
        header.pack_end(export_button)
        about_button = Gtk.Button(icon_name="help-about-symbolic", tooltip_text="About JW Calendar")
        self._accessible_name(about_button, "About JW Calendar")
        about_button.connect("clicked", self._show_about)
        header.pack_end(about_button)

        self._add_action("export-html", self._choose_html_export)
        self._add_action("export-csv", self._choose_csv_export)

        self._build_month_page()
        self._build_year_page()
        self._build_converter_page()
        self._build_help_page()
        for number, page in enumerate(("month", "year", "convert", "help"), start=1):
            self._add_action(f"show-{page}", lambda page=page: self.stack.set_visible_child_name(page))
            self.get_application().set_accels_for_action(f"win.show-{page}", [f"<Control>{number}"])
        toolbar.set_content(self.stack)
        self.set_content(toolbar)

    def _add_action(self, name: str, callback) -> None:
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", lambda *_: callback())
        self.add_action(action)

    def _build_month_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        page.set_margin_top(22)
        page.set_margin_bottom(22)
        page.set_margin_start(24)
        page.set_margin_end(24)

        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self._month_spin = Gtk.SpinButton.new_with_range(1, 9999, 1)
        self._month_spin.set_value(self._year)
        self._month_spin.set_numeric(True)
        self._month_spin.set_tooltip_text("Calendar year (1 to 9999)")
        self._month_dropdown = Gtk.DropDown.new_from_strings(self._month_names)
        self._month_dropdown.set_selected(self._month - 1)
        self._month_kind = Gtk.DropDown.new_from_strings(["Gregorian", "Julian"])
        self._week_dropdown = Gtk.DropDown.new_from_strings(["Sunday start", "Monday start"])
        self._week_dropdown.set_selected(0)
        for label, widget in (
            ("Year", self._month_spin),
            ("Month", self._month_dropdown),
            ("Calendar", self._month_kind),
            ("Week begins", self._week_dropdown),
        ):
            controls.append(self._labeled_control(label, widget))

        navigation = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        back = Gtk.Button(icon_name="go-previous-symbolic", tooltip_text="Previous month")
        forward = Gtk.Button(icon_name="go-next-symbolic", tooltip_text="Next month")
        self._accessible_name(back, "Previous month")
        self._accessible_name(forward, "Next month")
        back.connect("clicked", lambda *_: self._shift_month(-1))
        forward.connect("clicked", lambda *_: self._shift_month(1))
        navigation.append(back)
        navigation.append(forward)
        today = Gtk.Button(label="Today")
        today.set_tooltip_text("Go to today's date")
        today.connect("clicked", self._go_to_today)
        navigation.append(today)
        controls.append(navigation)
        page.append(controls)

        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        content.set_vexpand(True)
        self._calendar_grid = Gtk.Grid(column_spacing=4, row_spacing=4)
        self._calendar_grid.set_column_homogeneous(True)
        self._calendar_grid.set_hexpand(True)
        self._calendar_grid.set_vexpand(True)
        content.append(self._calendar_grid)

        details = Adw.PreferencesGroup(title="Selected date")
        details.set_size_request(270, -1)
        self._detail_label = Gtk.Label(xalign=0, yalign=0)
        self._detail_label.set_wrap(True)
        self._detail_label.set_selectable(True)
        self._detail_label.set_margin_top(6)
        details.add(self._detail_label)
        content.append(details)
        page.append(content)
        self.stack.add_titled_with_icon(page, "month", "Month", "x-office-calendar-symbolic")

        self._month_spin.connect("value-changed", self._month_control_changed)
        self._month_dropdown.connect("notify::selected", self._month_control_changed)
        self._month_kind.connect("notify::selected", self._month_control_changed)
        self._week_dropdown.connect("notify::selected", self._month_control_changed)

    @staticmethod
    def _accessible_name(widget: Gtk.Widget, name: str) -> None:
        widget.update_property([Gtk.AccessibleProperty.LABEL], [name])

    @staticmethod
    def _labeled_control(title: str, widget: Gtk.Widget) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        label = Gtk.Label(label=title, xalign=0)
        label.add_css_class("caption")
        CalendarWindow._accessible_name(widget, title)
        label.set_mnemonic_widget(widget)
        box.append(label)
        box.append(widget)
        return box

    def _build_year_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        page.set_margin_top(6)
        page.set_margin_bottom(6)
        page.set_margin_start(24)
        page.set_margin_end(24)
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self._year_spin = Gtk.SpinButton.new_with_range(1, 9999, 1)
        self._year_spin.set_value(self._year)
        self._year_kind = Gtk.DropDown.new_from_strings(["Gregorian", "Julian"])
        controls.append(self._labeled_control("Year", self._year_spin))
        controls.append(self._labeled_control("Calendar", self._year_kind))
        page.append(controls)
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        self._year_grid = Gtk.Grid(column_spacing=14, row_spacing=4)
        self._year_grid.set_column_homogeneous(True)
        scroller.set_child(self._year_grid)
        page.append(scroller)
        self.stack.add_titled_with_icon(page, "year", "Year", "view-grid-symbolic")
        self._year_spin.connect("value-changed", self._year_control_changed)
        self._year_kind.connect("notify::selected", self._year_control_changed)

    def _build_converter_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        page.set_margin_top(28)
        page.set_margin_bottom(24)
        page.set_margin_start(30)
        page.set_margin_end(30)
        group = Adw.PreferencesGroup(title="Gregorian and Julian conversion")
        group.set_description("Convert civil dates by their absolute day. Julian Day Number is shown separately.")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._converter_entry = Gtk.Entry(placeholder_text="YYYY-MM-DD")
        self._converter_entry.set_text("2027-01-01")
        self._converter_kind = Gtk.DropDown.new_from_strings(["Gregorian", "Julian"])
        self._accessible_name(self._converter_entry, "Date to convert, YYYY-MM-DD")
        self._accessible_name(self._converter_kind, "Conversion source calendar")
        self._converter_entry.connect("activate", self._convert_date)
        convert_button = Gtk.Button(label="Convert")
        convert_button.add_css_class("suggested-action")
        convert_button.connect("clicked", self._convert_date)
        row.append(self._converter_entry)
        row.append(self._converter_kind)
        row.append(convert_button)
        group.add(row)
        self._converter_result = Gtk.Label(label="Enter a valid date to see its equivalent.", xalign=0)
        self._converter_result.set_selectable(True)
        self._converter_result.set_wrap(True)
        group.add(self._converter_result)
        page.append(group)

        difference = Adw.PreferencesGroup(title="Date difference")
        difference.set_description("Count elapsed civil days between two dates; the second date is not counted as an extra day.")
        diff_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._difference_start = Gtk.Entry(placeholder_text="Start: YYYY-MM-DD")
        self._difference_start.set_text("2027-01-01")
        self._difference_end = Gtk.Entry(placeholder_text="End: YYYY-MM-DD")
        self._difference_end.set_text("2027-12-31")
        self._difference_kind = Gtk.DropDown.new_from_strings(["Gregorian", "Julian"])
        self._accessible_name(self._difference_start, "Start date, YYYY-MM-DD")
        self._accessible_name(self._difference_end, "End date, YYYY-MM-DD")
        self._accessible_name(self._difference_kind, "Date difference calendar")
        self._difference_end.connect("activate", self._calculate_difference)
        diff_button = Gtk.Button(label="Calculate")
        diff_button.connect("clicked", self._calculate_difference)
        diff_row.append(self._difference_start)
        diff_row.append(self._difference_end)
        diff_row.append(self._difference_kind)
        diff_row.append(diff_button)
        difference.add(diff_row)
        self._difference_result = Gtk.Label(label="364 elapsed days", xalign=0)
        self._difference_result.set_selectable(True)
        difference.add(self._difference_result)
        page.append(difference)
        self.stack.add_titled_with_icon(page, "convert", "Convert", "accessories-calculator-symbolic")

    def _build_help_page(self) -> None:
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        page.set_margin_top(28)
        page.set_margin_bottom(28)
        page.set_margin_start(30)
        page.set_margin_end(30)
        intro = Adw.StatusPage(
            title="Calendar reference, offline",
            description=(
                "Browse Gregorian and Julian civil dates, inspect ISO week and day-of-year "
                "details, convert dates, and export print-ready month layouts."
            ),
            icon_name="x-office-calendar-symbolic",
        )
        intro.set_vexpand(True)
        page.append(intro)
        intro.set_title("")
        intro.set_description("")
        intro_title = Gtk.Label(label="Calendar reference, offline", xalign=0)
        intro_title.add_css_class("title-2")
        page.append(intro_title)
        intro_description = Gtk.Label(label="Browse Gregorian and Julian dates, convert calendars, and export print-ready month layouts.", xalign=0, wrap=True)
        intro_description.add_css_class("dim-label")
        page.append(intro_description)
        appearance = Adw.PreferencesGroup(title="Appearance")
        appearance.set_description("Follow the desktop, or choose a light or dark window theme.")
        self._appearance_dropdown = Gtk.DropDown.new_from_strings(["System", "Light", "Dark"])
        appearance.add(self._labeled_control("Color scheme", self._appearance_dropdown))
        self._appearance_dropdown.connect("notify::selected", self._appearance_changed)
        page.append(appearance)
        help_row = Gtk.Label(
            label="In Month: ← / → changes month; Ctrl+← / Ctrl+→ changes year. Ctrl+1–4 opens Month, Year, Convert, Help.\n"
            "Use Export to save the current month as a print-ready HTML page or CSV file.",
            xalign=0,
            justify=Gtk.Justification.LEFT,
        )
        help_row.set_wrap(True)
        page.append(help_row)
        resources = Adw.PreferencesGroup(title="JW Calendar resources")
        resources.set_description("Open the project's calendar references in your web browser.")
        for label, uri in (
            ("2027 calendar reference", "https://jwcalendar.com/yearly-calendar/"),
            ("Julian calendar reference", "https://jwcalendar.com/julian-calendar/"),
            ("United States holidays", "https://jwcalendar.com/holidays/"),
        ):
            resources.add(Gtk.LinkButton.new_with_label(uri, label))
        page.append(resources)
        self.stack.add_titled_with_icon(page, "help", "Help", "help-about-symbolic")

    def _go_to_today(self, *_args) -> None:
        today = date.today()
        self._year, self._month = today.year, today.month
        self._selected_date = today.isoformat()
        self._syncing_controls = True
        self._month_spin.set_value(self._year)
        self._month_dropdown.set_selected(self._month - 1)
        self._year_spin.set_value(self._year)
        self._syncing_controls = False
        self._render_month()
        self._render_year()
        self._render_details()

    def _month_control_changed(self, *_args) -> None:
        if self._syncing_controls:
            return
        self._year = int(self._month_spin.get_value())
        self._month = self._month_dropdown.get_selected() + 1
        self._kind = "gregorian" if self._month_kind.get_selected() == 0 else "julian"
        self._week_start = "sunday" if self._week_dropdown.get_selected() == 0 else "monday"
        self._syncing_controls = True
        self._year_spin.set_value(self._year)
        self._year_kind.set_selected(self._month_kind.get_selected())
        self._syncing_controls = False
        self._selected_date = f"{self._year:04d}-{self._month:02d}-01"
        self._render_month()
        self._render_year()
        self._render_details()

    def _year_control_changed(self, *_args) -> None:
        if self._syncing_controls:
            return
        self._year = int(self._year_spin.get_value())
        self._syncing_controls = True
        self._month_spin.set_value(self._year)
        self._month_kind.set_selected(self._year_kind.get_selected())
        self._syncing_controls = False
        self._kind = "gregorian" if self._year_kind.get_selected() == 0 else "julian"
        self._selected_date = f"{self._year:04d}-{self._month:02d}-01"
        self._render_year()
        self._render_month()
        self._render_details()

    def _render_month(self) -> None:
        self._clear(self._calendar_grid)
        first_weekday = 0 if self._week_start == "monday" else 6
        days = self._weekdays[first_weekday:] + self._weekdays[:first_weekday]
        week_header = Gtk.Label(label="ISO week")
        week_header.add_css_class("caption")
        self._calendar_grid.attach(week_header, 0, 0, 1, 1)
        for col, label in enumerate(days, start=1):
            heading = Gtk.Label(label=label)
            heading.add_css_class("heading")
            self._calendar_grid.attach(heading, col, 0, 1, 1)
        rows = month_cells(
            self._year, self._month, kind=self._kind, week_start=self._week_start
        )
        for row_index, row in enumerate(rows, start=1):
            week_label = Gtk.Label(label=row[0].iso_week or "—")
            week_label.add_css_class("caption")
            self._calendar_grid.attach(week_label, 0, row_index, 1, 1)
            for col, cell in enumerate(row, start=1):
                if cell.date is None:
                    button = Gtk.Button(label="")
                    button.set_sensitive(False)
                else:
                    button = Gtk.Button(label=str(cell.date.day))
                    button.add_css_class("flat")
                    button.set_hexpand(True)
                    button.set_size_request(-1, 44)
                    details = date_details(cell.date)
                    is_selected = iso_date(cell.date) == self._selected_date
                    accessible_description = (
                        f"{'Selected date, ' if is_selected else ''}"
                        f"{details['weekday']}, {iso_date(cell.date)}, "
                        f"{self._kind}, ISO week {cell.iso_week}"
                    )
                    button.set_tooltip_text(accessible_description)
                    button.update_property(
                        [Gtk.AccessibleProperty.DESCRIPTION], [accessible_description]
                    )
                    button.update_state(
                        [Gtk.AccessibleState.SELECTED],
                        [is_selected],
                    )
                    if not cell.in_month:
                        button.add_css_class("dim-label")
                    if is_selected:
                        button.add_css_class("suggested-action")
                        button.remove_css_class("flat")
                    button.connect("clicked", self._select_date, cell.date)
                self._calendar_grid.attach(button, col, row_index, 1, 1)

    def _render_year(self) -> None:
        self._clear(self._year_grid)
        kind: CalendarKind = "gregorian" if self._year_kind.get_selected() == 0 else "julian"
        for month in range(1, 13):
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            card.add_css_class("card")
            title = Gtk.Label(label=calendar.month_name[month], xalign=0)
            title.add_css_class("heading")
            card.append(title)
            mini = Gtk.Grid(column_spacing=2, row_spacing=1)
            mini.set_column_homogeneous(True)
            first_weekday = 0 if self._week_start == "monday" else 6
            labels = self._weekdays[first_weekday:] + self._weekdays[:first_weekday]
            for col, name in enumerate(labels):
                label = Gtk.Label(label=name[:1])
                label.add_css_class("caption")
                mini.attach(label, col, 0, 1, 1)
            rows = month_cells(self._year, month, kind=kind, week_start=self._week_start)
            for r, row in enumerate(rows, start=1):
                for col, cell in enumerate(row):
                    label = Gtk.Label(label=str(cell.date.day) if cell.date else "")
                    if cell.date and not cell.in_month:
                        label.add_css_class("dim-label")
                    mini.attach(label, col, r, 1, 1)
            card.append(mini)
            self._year_grid.attach(card, (month - 1) % 3, (month - 1) // 3, 1, 1)

    def _render_details(self) -> None:
        try:
            details = date_details(parse_date(self._selected_date, self._kind))
            lines = [
                f"<b>{details['weekday']}, {details['date']} ({details['calendar']})</b>",
                f"Gregorian: {details['gregorian']}",
                f"Julian: {details['julian']}",
                f"ISO week: {details['iso_week']}",
                f"Day of year: {details['ordinal']}",
                f"Julian Day Number: {details['jdn']}",
                f"Leap year: {'Yes' if details['leap_year'] == 'True' else 'No'}",
            ]
            self._detail_label.set_markup("\n\n".join(lines))
        except ValueError:
            self._detail_label.set_text("Select a date within the displayed month.")

    def _select_date(self, _button: Gtk.Button, value) -> None:
        restore_focus = _button is not None and _button.has_focus()
        self._selected_date = iso_date(value)
        self._year, self._month = value.year, value.month
        self._syncing_controls = True
        self._month_spin.set_value(self._year)
        self._month_dropdown.set_selected(self._month - 1)
        self._year_spin.set_value(self._year)
        self._syncing_controls = False
        self._render_month()
        self._render_year()
        self._render_details()
        if restore_focus:
            child = self._calendar_grid.get_first_child()
            while child is not None:
                if isinstance(child, Gtk.Button) and child.has_css_class("suggested-action"):
                    child.grab_focus()
                    break
                child = child.get_next_sibling()

    def _shift_month(self, amount: int) -> None:
        index = self._year * 12 + self._month - 1 + amount
        year, month0 = divmod(index, 12)
        year += 0
        if 1 <= year <= 9999:
            self._year, self._month = year, month0 + 1
            self._month_spin.set_value(year)
            self._month_dropdown.set_selected(month0)

    def _convert_date(self, *_args) -> None:
        try:
            kind: CalendarKind = "gregorian" if self._converter_kind.get_selected() == 0 else "julian"
            details = date_details(parse_date(self._converter_entry.get_text(), kind))
            self._converter_result.set_text(
                f"Gregorian: {details['gregorian']}\n"
                f"Julian: {details['julian']}\n"
                f"ISO week: {details['iso_week']}  ·  Day of year: {details['ordinal']}\n"
                f"Julian Day Number: {details['jdn']}"
            )
        except ValueError as error:
            self._converter_result.set_text(str(error))

    def _calculate_difference(self, *_args) -> None:
        kind: CalendarKind = "gregorian" if self._difference_kind.get_selected() == 0 else "julian"
        try:
            amount = days_between_dates(
                self._difference_start.get_text(), self._difference_end.get_text(), kind=kind
            )
            self._difference_result.set_text(f"{amount} elapsed civil days")
        except ValueError as error:
            self._difference_result.set_text(str(error))

    def _appearance_changed(self, *_args) -> None:
        style = Adw.StyleManager.get_default()
        scheme = self._appearance_dropdown.get_selected()
        if scheme == 1:
            style.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        elif scheme == 2:
            style.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        else:
            style.set_color_scheme(Adw.ColorScheme.DEFAULT)

    def _copy_date(self, *_args) -> None:
        display = Gdk.Display.get_default()
        if display:
            provider = Gdk.ContentProvider.new_for_value(self._selected_date)
            display.get_clipboard().set_content(provider)

    def _choose_html_export(self) -> None:
        content = month_html(
            self._year, self._month, kind=self._kind, week_start=self._week_start
        )
        self._save_file(content, f"{calendar.month_name[self._month].lower()}-{self._year}.html")

    def _choose_csv_export(self) -> None:
        content = month_csv(
            self._year, self._month, kind=self._kind, week_start=self._week_start
        )
        self._save_file(content, f"{calendar.month_name[self._month].lower()}-{self._year}.csv")

    def _save_file(self, content: str, filename: str) -> None:
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export calendar")
        dialog.set_initial_name(filename)
        self._active_chooser = dialog

        def selected(source, result, _user_data=None):
            try:
                file = source.save_finish(result)
            except GLib.Error as error:
                self._active_chooser = None
                if error.matches(Gio.io_error_quark(), Gio.IOErrorEnum.CANCELLED):
                    return
                message = Adw.MessageDialog.new(self, "Could not choose export location", error.message)
                message.add_response("close", "Close")
                message.set_default_response("close")
                message.set_close_response("close")
                message.present()
                return
            self._active_chooser = None
            self._write_export(file, content)

        dialog.save(self, None, selected)

    def _write_export(self, file: Gio.File, content: str, completed=None) -> None:
        def saved(source, result, _user_data=None):
            error = None
            try:
                source.replace_contents_finish(result)
            except GLib.Error as caught:
                error = caught
                if completed is None:
                    message = Adw.MessageDialog.new(self, "Could not save calendar", caught.message)
                    message.add_response("close", "Close")
                    message.set_default_response("close")
                    message.set_close_response("close")
                    message.present()
            if completed:
                completed(error)

        file.replace_contents_bytes_async(
            GLib.Bytes.new(content.encode("utf-8")), None, False,
            Gio.FileCreateFlags.NONE, None, saved,
        )

    def _show_about(self, *_args) -> None:
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="JW Calendar",
            application_icon="com.jwcalendar.JWCalendar",
            developer_name="Karen Cohen",
            version=self._version,
            comments="An offline Gregorian and Julian calendar reference.",
            website="https://jwcalendar.com/",
            license_type=Gtk.License.MIT_X11,
        )
        about.present()

    def _on_key_pressed(self, _controller, keyval, _keycode, state) -> bool:
        focus = self.get_focus()
        if self.stack.get_visible_child_name() != "month":
            return False
        while focus is not None and focus is not self:
            if isinstance(focus, (Gtk.Editable, Gtk.SpinButton, Gtk.DropDown)):
                return False
            focus = focus.get_parent()
        if keyval == Gdk.KEY_Left:
            self._shift_month(-12 if state & Gdk.ModifierType.CONTROL_MASK else -1)
            return True
        if keyval == Gdk.KEY_Right:
            self._shift_month(12 if state & Gdk.ModifierType.CONTROL_MASK else 1)
            return True
        return False

    @staticmethod
    def _clear(container: Gtk.Grid) -> None:
        child = container.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            container.remove(child)
            child = next_child

# JW Calendar

JW Calendar is an offline Gregorian and Julian calendar and date utility. It includes both a command-line interface and a GTK 4/libadwaita desktop application. Calendar calculations do not need an account or network access.

The official project website is [jwcalendar.com](https://jwcalendar.com/). This application uses the separately published [`jwcalendar-calendrical`](https://github.com/karencohenjw/jwcalendar-calendrical) Python library for its date arithmetic and month grids.

## Features

- Browse Gregorian or Julian months and full years.
- Choose Sunday or Monday as the first day of the week.
- Inspect weekday, day of year, ISO week, Gregorian and Julian equivalents, leap-year status, and Julian Day Number.
- Convert dates between Gregorian and Julian calendars.
- Calculate elapsed days between dates.
- Copy the selected date, or export a month as CSV or print-ready, self-contained HTML.
- Use system, light, or dark color schemes, keyboard month/year navigation, and the native desktop file chooser.
- List United States federal statutory and observed holidays from the CLI.
- Run offline without login, advertising, telemetry, or network permissions.

## Status and platforms

The first public release is [JW Calendar 0.1.0](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.0). Linux with GTK 4 and libadwaita 1.4 or newer is the intended platform; macOS and Windows are not supported. A Flatpak package has not been prepared or submitted.

The initial repository contents were created with substantial AI assistance; see [AI-ASSISTANCE.md](AI-ASSISTANCE.md). The project owner should review the code and continue maintaining the project before making further releases.

## Run from a source checkout

Install Python 3.10+, GTK 4 development bindings, PyGObject, and libadwaita 1.4+ from your Linux distribution. Then:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
jwcalendar --help
jwcalendar month 2027-01 --week-start monday
jwcalendar date 2028-02-29 --json
jwcalendar convert 1582-10-04 --from julian
jwcalendar difference 2026-12-31 2027-01-01
jwcalendar holidays 2027
jw-calendar-desktop
```

Install GTK 4, libadwaita, and PyGObject from your Linux distribution to use the desktop interface. The command-line tool only needs the Python package. The calendar engine dependency is downloaded from PyPI during a development install. A future Flatpak build must stage every source before its offline build phase; this repository intentionally does not include a Flatpak manifest.

CSV and HTML are printed to standard output when requested with `month --csv` or `month --html`; the desktop app opens a save dialog for exports. The HTML output is self-contained and has print styles.

The holiday command covers the 11 nationwide United States federal holidays under 5 USC 6103, with separate statutory and observed dates. It does not include state/local holidays or one-off federal closures. Dates are civil calendar dates; timezone offsets do not alter an explicitly supplied date.

## Calendar models

The Gregorian and Julian calendars are extended proleptically within the engine's supported years 1–9999. Historical adoption of the Gregorian reform differed by region; conversion here aligns both date labels to the same absolute day and does not model local historical adoption. “Julian date” means a Julian civil calendar date. Julian Day Number is a separate integer day count.

ISO week dates follow ISO 8601 and may have a week-year different from the Gregorian calendar year.

## Keyboard shortcuts

- Left/right arrow: previous/next month.
- Ctrl+left/Ctrl+right: previous/next year.
- Today button: return to the current local civil date.

## Privacy and accessibility

Calendar calculations run locally. The desktop app opens selected JW Calendar help references in the system browser only when clicked. It writes export files only after the user selects a destination. See [docs/ACCESSIBILITY.md](docs/ACCESSIBILITY.md) for supported interaction and remaining review work.

## Tests

```sh
python -m unittest discover -s tests -v
```

Pure calendar and export tests do not need a display. The optional window smoke test runs when GTK 4, libadwaita, and a graphical display (or Xvfb) are available.

## Architecture

- `src/jwcalendar_desktop/core.py` adapts the published calendrical engine into display rows, date details, CSV, and print HTML.
- `src/jwcalendar_desktop/window.py` builds the native GTK 4/libadwaita interface.
- `src/jwcalendar_desktop/cli.py` implements `jwcalendar` without importing GTK.
- `src/jwcalendar_desktop/app.py` registers the desktop application.
- `data/` contains the upstream launcher, icon, and AppStream metadata.

The application performs calculations locally. It writes exports only to a file explicitly selected by the user through the desktop save dialog.

## Build a wheel

```sh
python -m pip install build
python -m build
```

## License

The application code and original project assets are distributed under the MIT License. The separately packaged calendrical engine retains its own license and provenance.

# Contributing

Contributions should improve calendar correctness, accessibility, usability, or maintainability. Describe the user effect and include regression coverage for calculation changes. Keep changes focused; no special contribution agreement is required.

## Clone and install

Use Python 3.10 or newer, GTK 4.10 or newer, PyGObject, and libadwaita 1.4 or newer. Install GTK and Python GObject bindings from your Linux distribution, then:

```sh
git clone https://github.com/karencohenjw/jw-calendar-desktop.git
cd jw-calendar-desktop
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

The app depends on the separately published `jwcalendar-calendrical==0.1.0` package. The CLI runs with Python alone; the desktop window needs the system GTK bindings. No account or network connection is needed for calendar functions.

## Run and check

```sh
python -m unittest discover -s tests -v
jwcalendar --help
jw-calendar-desktop
python -m pip install build
python -m build
```

The Linux GUI workflow is available from GitHub Actions (`Linux GUI QA`). It exercises the live GTK interface through AT-SPI, checks file export and AppStream, runs a forced-portal readiness check, and repeats core GUI/export behavior with networking disabled. Run it on a normal Linux desktop when working on focus, speech, theme, or window layout. The GTK smoke tests skip when GTK bindings or a display are unavailable.

## Project map

- `src/jwcalendar_desktop/core.py` adapts the calendrical engine into calendar rows, date details, CSV, and printable HTML.
- `src/jwcalendar_desktop/window.py` builds the GTK 4/libadwaita desktop UI and GIO exports.
- `src/jwcalendar_desktop/cli.py` implements the CLI without loading GTK.
- `src/jwcalendar_desktop/app.py` launches the desktop application.
- `data/` holds the desktop launcher, icon, screenshots, and AppStream metadata.
- `tests/` contains calendar, CLI, holiday, and optional GTK integration tests.
- `.github/workflows/` has the routine test/build and Linux GUI checks.

Gregorian and Julian civil dates refer to the same absolute days; a Julian civil date is different from a Julian Day Number. The engine supports years 1–9999. Preserve those distinctions and test leap years, centuries, calendar boundaries, and ISO week-year boundaries when changing calendar behavior.

## Upstream releases

Follow [the release checklist](docs/RELEASE-CHECKLIST.md). Releases represent reviewed, tested project states; do not add tags or claim downloads to create activity. Keep `CHANGELOG.md`, the package version, desktop metadata, and AppStream release notes consistent.

## AI assistance

Disclose AI-assisted upstream contributions in `AI-ASSISTANCE.md` and keep it accurate. Human maintainers remain responsible for correctness and provenance. Flathub manifests and Flathub submission communications must be human-authored under the current policy.

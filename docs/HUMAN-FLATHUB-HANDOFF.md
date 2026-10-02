# Human Flathub packaging handoff

This document is a factual checklist, not a Flatpak manifest. No Flatpak or dependency manifest is included in this project.

## Application facts

- Application ID: `com.jwcalendar.JWCalendar`
- Upstream: https://github.com/karencohenjw/jw-calendar-desktop
- Current stable release: [`v0.1.1`](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.1), tagged at `2015d95145c08a16e23ee1cb63639cadbd8a6691`. Earlier release `v0.1.0` is commit `7a42fa52c450a5c8b14827d5b858f0631c8a42d1`; its archive SHA-256 is `2a70a3bdacd8f1b465d56e9398db951446f9de4093126199f32ac1ac55edebb1`.
- License: MIT; see `LICENSE`.
- CLI executable: `jwcalendar`
- Desktop executable: `jw-calendar-desktop`
- Desktop file: `com.jwcalendar.JWCalendar.desktop`
- AppStream file: `com.jwcalendar.JWCalendar.metainfo.xml`
- Installed icon name: `com.jwcalendar.JWCalendar` (scalable SVG). Size-test PNG renders are kept in `data/icons/` but are not installed by the Python package.
- Python package: `jwcalendar-calendrical==0.1.0`, MIT; verified source archive and SHA-256 are in `DEPENDENCIES.md`.
- Network permission for core behavior: not needed.
- Broad home/host filesystem access: not needed. User-selected export destinations should use a portal.
- The `v0.1.1` release commit is `2015d95145c08a16e23ee1cb63639cadbd8a6691`; current public `main` descends from it. The verified development branch is [`codex/flathub-readiness-draft`](https://github.com/karencohenjw/jw-calendar-desktop/tree/codex/flathub-readiness-draft). Screenshot commit `d45faa0fd23d75554c87e0e182bf757de6ca88a8` and all later work preserve ancestry.
- Architectures tested: macOS arm64 Python unit suite, plus Linux amd64 Python 3.10–3.13, GTK/Xvfb, AppStream, desktop integration, and strict Snap build checks. Main CI [#37053336902](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37053336902) and release-tag CI [#37053841406](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37053841406) passed. GUI QA [#37052977644](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37052977644) verified both real file exports. Xvfb is not a substitute for visual review on a real Linux desktop.
- Clean public checkout: the `v0.1.0` tag was cloned into a new empty directory. Python 3.12 `pip install .` built and installed the package; `python -m build` produced an sdist and wheel. The latest local run passed 25 tests; 2 GTK display tests skipped because macOS has no display. The v0.1.1 Linux CI passed GTK/Xvfb, AppStream, desktop-file, packaging, and strict amd64 Snap checks on `2015d95`; the release metadata passed AppStream validation.
- Real Linux screenshots: four genuine, unedited 960 × 700 captures from Ubuntu 24.04.5 LTS, Python 3.12.3, GTK 4.14.5, and libadwaita 1.5.0. They show January 2027 details, the full 2027 view, Gregorian/Julian conversion and date difference, and Help. They are public from screenshot commit `d45faa0fd23d75554c87e0e182bf757de6ca88a8`. AppStream references these immutable raw image URLs:
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/month-view.png
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/year-view.png
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/convert-view.png
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/help-view.png

## Runtime and source research snapshot — 2026-10-02

Flathub's runtime documentation currently lists the GNOME runtime, and the current GNOME application platform listing is version 50. A new submission must re-check the newest hosted GNOME runtime and matching SDK immediately before packaging; this snapshot is not a permanent recommendation. GTK 4 and libadwaita are expected from a compatible GNOME runtime. The packager must verify whether that exact runtime provides a compatible Python interpreter and PyGObject; otherwise source and build the missing binding compatibly.

Flathub's Python source workflow is commonly handled with `flatpak-pip-generator` from `flatpak-builder-tools`. A human must run the current supported tool, review all generated dependency sources, versions, licenses and hashes, and keep the generated output out of AI-authored project changes.

## Portal behavior and permissions

The application uses `Gtk.FileChooserNative` for user-directed file exports and normal GTK clipboard APIs. The GTK chooser visibly opened and cancellation worked. GUI QA run #37052977644 verified non-empty CSV and HTML files, parsed the CSV, checked the January 2027 HTML table, and confirmed the HTML has no remote resources. GTK can route its native chooser through XDG Desktop Portal in a sandbox, but a real Flatpak portal sandbox has not been built or tested. The GTK clipboard API is exercised in CI; paste into a separate Linux editor was not verified. Offline behavior has not been tested with network physically disabled, although the application source has no network client and core use is designed to be offline. Do not grant broad filesystem or network access.

## Human work before submission

- Build sustained project history and evidence of maintenance/use; all current commits belong to the initial same-day setup.
- Final Linux CI, desktop/AppStream validation, and public `v0.1.1` release have passed; verify future releases from a clean checkout.
- The screenshots are public and AppStream image URLs are pinned to screenshot commit `d45faa0fd23d75554c87e0e182bf757de6ca88a8`.
- GUI file saving and CSV/HTML content checks passed in run #37052977644; a real Flatpak portal sandbox check remains.
- Re-check the current runtime, SDK, policies, package sources, licenses, and domain proof.
- Have a human create and review all packaging files, run the offline build and linters, and perform local install/run checks.
- Human must perform all Flathub submission and reviewer communication. This project task did not create or submit anything there.

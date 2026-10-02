# Human Flathub packaging handoff

This document is a factual checklist, not a Flatpak manifest. No Flatpak or dependency manifest is included in this project.

## Application facts

- Application ID: `com.jwcalendar.JWCalendar`
- Upstream: https://github.com/karencohenjw/jw-calendar-desktop
- Stable tag: `v0.1.0` (commit `7a42fa52c450a5c8b14827d5b858f0631c8a42d1`). Source archive: https://github.com/karencohenjw/jw-calendar-desktop/archive/refs/tags/v0.1.0.tar.gz. SHA-256 of the downloaded GitHub archive: `2a70a3bdacd8f1b465d56e9398db951446f9de4093126199f32ac1ac55edebb1`.
- License: MIT; see `LICENSE`.
- CLI executable: `jwcalendar`
- Desktop executable: `jw-calendar-desktop`
- Desktop file: `com.jwcalendar.JWCalendar.desktop`
- AppStream file: `com.jwcalendar.JWCalendar.metainfo.xml`
- Installed icon name: `com.jwcalendar.JWCalendar` (scalable SVG). Size-test PNG renders are kept in `data/icons/` but are not installed by the Python package.
- Python package: `jwcalendar-calendrical==0.1.0`, MIT; verified source archive and SHA-256 are in `DEPENDENCIES.md`.
- Network permission for core behavior: not needed.
- Broad home/host filesystem access: not needed. User-selected export destinations should use a portal.
- Current public upstream commit: `efe266cf3108950d1ae1760763c00560ad7f02df`. Local unpublished screenshot commit: `d45faa0fd23d75554c87e0e182bf757de6ca88a8`; it must be pushed before its raw URLs resolve. The following local readiness commit is `c67e09c` and is also unpublished.
- Architectures tested: macOS arm64 Python unit suite, plus Linux amd64 Python, GTK/Xvfb, metadata, and Snap build checks in GitHub Actions. Linux CI #50 on public commit `efe266c` passed. Linux GUI QA #14 opened and cancelled the native chooser, then failed its CSV file-save assertion. Xvfb is not a substitute for visual review on a real Linux desktop.
- Clean public checkout: the `v0.1.0` tag was cloned into a new empty directory. Python 3.12 `pip install .` built and installed the package; `python -m build` produced an sdist and wheel. The latest local run passed 25 tests; 2 GTK display tests skipped because macOS has no display. The public Linux CI passed GTK/Xvfb, AppStream, desktop-file, packaging, and stable-grade amd64 Snap checks on `efe266c`. The local `0.1.1` AppStream draft has only been XML-parsed; it has not yet passed Linux AppStream validation.
- Real Linux screenshots: four genuine, unedited 960 × 700 captures from Ubuntu 24.04.5 LTS, Python 3.12.3, GTK 4.14.5, and libadwaita 1.5.0. They show January 2027 details, the full 2027 view, Gregorian/Julian conversion and date difference, and Help. They are local only until the screenshot commit is pushed. Intended immutable image URLs, pinned to `d45faa0fd23d75554c87e0e182bf757de6ca88a8`:
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/month-view.png
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/year-view.png
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/convert-view.png
  - https://raw.githubusercontent.com/karencohenjw/jw-calendar-desktop/d45faa0fd23d75554c87e0e182bf757de6ca88a8/data/screenshots/help-view.png

## Runtime and source research snapshot — 2026-10-02

Flathub's runtime documentation currently lists the GNOME runtime, and the current GNOME application platform listing is version 50. A new submission must re-check the newest hosted GNOME runtime and matching SDK immediately before packaging; this snapshot is not a permanent recommendation. GTK 4 and libadwaita are expected from a compatible GNOME runtime. The packager must verify whether that exact runtime provides a compatible Python interpreter and PyGObject; otherwise source and build the missing binding compatibly.

Flathub's Python source workflow is commonly handled with `flatpak-pip-generator` from `flatpak-builder-tools`. A human must run the current supported tool, review all generated dependency sources, versions, licenses and hashes, and keep the generated output out of AI-authored project changes.

## Portal behavior and permissions

The application uses `Gtk.FileChooserNative` for user-directed file exports and normal GTK clipboard APIs. The GTK chooser visibly opened and cancellation worked in Linux GUI QA; the save flow is not yet verified because run #14 failed before the CSV file assertion passed. The follow-up local GUI script now clicks the visible GTK Save button, but still needs an Ubuntu run. GTK can route its native chooser through XDG Desktop Portal in a sandbox, but a real Flatpak portal sandbox has not been built or tested. The GTK clipboard API is exercised in CI; paste into a separate Linux editor was not verified. Offline behavior has not been tested with network physically disabled, although the application source has no network client and core use is designed to be offline. Do not grant broad filesystem or network access.

## Human work before submission

- Build sustained project history and evidence of maintenance/use; all current commits belong to the initial same-day setup.
- Confirm the final Linux CI, desktop/AppStream validation, published source release, and clean public checkout.
- Push the local screenshot commit first; it records the actual SHA `d45faa0fd23d75554c87e0e182bf757de6ca88a8`. The local `0.1.1` AppStream screenshot URLs already use direct raw URLs pinned to that SHA. They will work only after that commit is public. Local AppStream release metadata and version bump are draft-only; public stable remains `v0.1.0`.
- Fix the GUI save automation and pass actual CSV/HTML write and content checks. The latest public GUI QA run confirmed chooser open/cancel but failed on the CSV save assertion.
- Re-check the current runtime, SDK, policies, package sources, licenses, and domain proof.
- Have a human create and review all packaging files, run the offline build and linters, and perform local install/run checks.
- Human must perform all Flathub submission and reviewer communication. This project task did not create or submit anything there.

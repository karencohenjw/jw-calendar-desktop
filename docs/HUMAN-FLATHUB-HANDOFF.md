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
- Architectures tested: macOS arm64 Python unit suite, plus Linux amd64 Python, GTK/Xvfb, metadata, and Snap build checks in GitHub Actions. Check the latest run and final release commit before treating them as release evidence. Xvfb is not a substitute for visual review on a real Linux desktop.
- Clean public checkout: the `v0.1.0` tag was cloned into a new empty directory. Python 3.12 `pip install .` built and installed the package; `python -m build` produced an sdist and wheel; 25 tests passed and 2 GTK display tests skipped locally. Linux CI passed the GTK/Xvfb tests and stable-grade amd64 Snap build.

## Runtime and source research snapshot — 2026-10-02

Flathub's runtime documentation currently lists the GNOME runtime, and the current GNOME application platform listing is version 50. A new submission must re-check the newest hosted GNOME runtime and matching SDK immediately before packaging; this snapshot is not a permanent recommendation. GTK 4 and libadwaita are expected from a compatible GNOME runtime. The packager must verify whether that exact runtime provides a compatible Python interpreter and PyGObject; otherwise source and build the missing binding compatibly.

Flathub's Python source workflow is commonly handled with `flatpak-pip-generator` from `flatpak-builder-tools`. A human must run the current supported tool, review all generated dependency sources, versions, licenses and hashes, and keep the generated output out of AI-authored project changes.

## Portal behavior and permissions

The application uses `Gtk.FileChooserNative` for user-directed file exports and normal GTK clipboard APIs. GTK can route its native chooser through XDG Desktop Portal in a sandbox, but this has not yet been verified in a real Linux sandbox. Do not grant broad filesystem or network access. Validate month navigation, conversion, date details, offline HTML/CSV generation, chooser save/cancel, and clipboard after packaging.

## Human work before submission

- Build sustained project history and evidence of maintenance/use; all current commits belong to the initial same-day setup.
- Confirm the final Linux CI, desktop/AppStream validation, published source release, and clean public checkout.
- Capture real Linux screenshots and publish them at immutable release URLs.
- Re-check the current runtime, SDK, policies, package sources, licenses, and domain proof.
- Have a human create and review all packaging files, run the offline build and linters, and perform local install/run checks.
- Human must perform all Flathub submission and reviewer communication. This project task did not create or submit anything there.

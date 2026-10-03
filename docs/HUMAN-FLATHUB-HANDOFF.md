# Human Linux packaging handoff

Reviewed 2026-10-03. This is upstream fact-finding for a future human packager. It contains no Flatpak manifest or generated dependency fragment.

## Verified source facts

- Application ID: `com.jwcalendar.JWCalendar`; upstream: https://github.com/karencohenjw/jw-calendar-desktop
- Latest published stable release at this review: [`v0.1.1`](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.1), tag `2015d95145c08a16e23ee1cb63639cadbd8a6691`. Remote `main` is `48acdda2459253de88d9c9ea290082d0531c5ed1`; the later upstream-hardening branch remains unreleased and has not yet been merged into `main`.
- Project license: MIT. MetaInfo license: CC0-1.0. Desktop ID: `com.jwcalendar.JWCalendar.desktop`.
- Executables: `jwcalendar` and `jw-calendar-desktop`; icon: `com.jwcalendar.JWCalendar` SVG.
- GTK requirement: 4.10+ for `Gtk.FileDialog`; libadwaita: 1.4+. GTK, PyGObject, and libadwaita are supplied by the Linux desktop/runtime, not Python dependencies.
- Only declared third-party Python runtime dependency: `jwcalendar-calendrical==0.1.0` (MIT, no runtime dependencies). The immutable PyPI source URL and SHA-256, plus the project's setuptools build requirement, are in `DEPENDENCIES.md`.
- Export receives the user-selected GIO file from GTK's file dialog and writes through GIO. GTK may use the XDG FileChooser portal. Clipboard uses the desktop clipboard. Calendar calculation, conversions, and both exporters have no network requirement.
- The hardening branch passed [Linux GUI QA run 37102312221](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37102312221), including live AT-SPI checks, a real desktop FileChooser portal call, export saves with networking disabled, and current Flathub AppStream lint. It is upstream portal-readiness evidence, not a Flatpak sandbox test.
- GitHub Private Vulnerability Reporting was enabled and confirmed in repository settings on 2026-10-02. See `SECURITY.md`.
- The Snap Store lists `jwcalendar` in the public stable channel at version `0.1.0` as of 2026-10-02; upstream's current GitHub release is `0.1.1`. No usage statistics were inferred from publication.

## Build and validate by a human

1. Re-check the latest hosted GNOME Platform and SDK; the 2026-10-03 research snapshot is GNOME 51.
2. Verify the Flathub application ID/domain through its current owner-verification process.
3. Review all source and provenance disclosures. The project had a short same-day history as of this review; don't represent that as sustained maintenance or user uptake.
4. Resolve the pinned Python dependency and every transitive/build dependency to reviewed licenses, immutable archives, and verified hashes. Make all sources available before building with network disabled.
5. Create and review a fully human-authored Flatpak package under the current policy. Keep permissions minimal and check the GTK portal in an actual Flatpak sandbox, including saved-file access after chooser return.
6. Run the GUI, CLI, output checks, keyboard/accessibility review, and Flathub's then-current AppStream and build linters. The upstream `Linux GUI QA` workflow is useful evidence but is not a Flatpak build or sandbox test.
7. Follow `HUMAN-FLATPAK-TEST-CHECKLIST.md`. The owner must handle any later Flathub verification, packaging submission, and communications.

No Flathub submission branch, manifest, submission PR, or reviewer response was created by this upstream task. See `FLATHUB-READINESS.md` for policy/history blockers and `RELEASE-CHECKLIST.md` for an upstream source release.

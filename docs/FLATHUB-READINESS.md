# Upstream and Flathub readiness

Reviewed 2026-10-03 against the live upstream repository and current Flathub documentation. This note describes source-project readiness; it is not a submission or package manifest.

## Current verification record

- Remote `main` is `48acdda2459253de88d9c9ea290082d0531c5ed1`. The hardening work is on `codex/upstream-hardening`; it is not yet part of that public `main` commit or a released version.
- The latest published stable release remains [`v0.1.1`](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.1), tag commit `2015d95145c08a16e23ee1cb63639cadbd8a6691`. No `v0.1.2` was created.
- The hardening branch passed [Linux GUI QA run 37102312221](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37102312221) at source commit `d9b00886ccb588a1f9e45cfb52cc389741e55d2e`. It exercised the visible GTK application, live AT-SPI keyboard behavior, a real FileChooser portal call, CSV and HTML saves in a network-disabled namespace, and the current Flathub AppStream linter.
- Four full-size reviewed application-window captures are pinned to screenshot asset commit `ab5e7d41b9b25bcf50fbe0bfdf22a76f60e5e0ad`. Details and limitations are in [SCREENSHOT-CHECKLIST.md](SCREENSHOT-CHECKLIST.md).

## Upstream technical readiness

- Stable upstream release: [`v0.1.1`](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.1), tag commit `2015d95145c08a16e23ee1cb63639cadbd8a6691`. Current `main` is checked independently; see the current CI run linked from its GitHub Actions page.
- The [Snap Store](https://snapcraft.io/jwcalendar) has a public `stable` channel, last observed at version `0.1.0` on 2026-10-02. That published package predates the latest upstream `v0.1.1`; no Snap Store install counts or individual users were inferred.
- Application ID `com.jwcalendar.JWCalendar`, installed desktop entry, scalable icon, English AppStream metadata, two executable names, MIT project license, CC0 metadata license, all-ages OARS rating, homepage, repository, and issue tracker are recorded in the source.
- AppStream's canonical summary is “Browse dates and calendars”. The desktop entry uses the same sentence. Release `0.1.0` is a stable first public release; its note no longer calls it a development release.
- MetaInfo advertises keyboard and pointing controls plus offline-only operation. It does not claim touch support. The AppStream `supports` relation is advisory metadata; it is not a device compatibility certification.
- Four English Linux window screenshots show real application content, with the month view first. Their dimensions and native window decoration are reviewed by the Linux GUI workflow; image URLs are pinned to the screenshot commit recorded in the metadata.
- GUI export uses GTK 4.10+ `Gtk.FileDialog`, obtains a `GFile`, and writes via GIO. GTK uses the desktop FileChooser portal when it is available. The GUI workflow forces GTK's portal path and records a D-Bus call from a normal, unsandboxed Linux session; this is a portal-readiness test, not Flatpak sandbox verification.
- Linux GUI/AT-SPI, actual network-disabled app/export, screenshot, and current Flathub AppStream linter results are produced by the manually run `Linux GUI QA` workflow. See [accessibility notes](ACCESSIBILITY.md) and [human packaging checklist](HUMAN-FLATPAK-TEST-CHECKLIST.md).
- The only external Python runtime dependency is `jwcalendar-calendrical==0.1.0` (MIT, no declared runtime dependencies). Its immutable PyPI source archive URL, SHA-256, build/runtime requirements, and verification notes are in [DEPENDENCIES.md](DEPENDENCIES.md). A human packager must stage all build sources before building without network.
- The current Flathub-hosted GNOME runtime and SDK research snapshot is **GNOME 51**, checked 2026-10-03: [runtime](https://flathub.org/en/apps/org.gnome.Platform) and [SDK](https://flathub.org/en/apps/org.gnome.Sdk). Re-check the latest hosted stable branch immediately before packaging; Flathub requires the latest hosted runtime at submission time.
- The SVG app icon and supplied 64, 128, and 256 pixel PNGs were inspected at native size and against light and dark backgrounds. The calendar mark remains recognizable, has clear contrast, and has no obvious padding or tiny-detail problem; no icon change was justified.
- Private Vulnerability Reporting was enabled on the repository's GitHub Advanced Security settings page on 2026-10-02. The public repository's Security → Advisories area is available for private reports. `SECURITY.md` documents this route and the current released version.
- No human-authored Flatpak manifest, build, or sandbox test is present. A normal Linux portal call does not validate sandbox permissions or document-portal persistence.

## Flathub policy and project history

- The public Git history began on 2026-10-02. The published `v0.1.1` release and the passing hardening-branch CI are authentic source history, but this short history does not demonstrate sustained maintenance or meaningful real-world use.
- No real user installs, organic usage, third-party package uptake, independent issue reports, or external contributions have been verified for this review. GitHub release download counters should be observed organically; they must not be manipulated. Real user reports, actual package installs, official-site references, and outside contributions may become useful evidence if they occur naturally.
- Flathub publishes no fixed minimum project age. Do not claim a required 30-day or three-month waiting period.
- The owner should review AI-assisted source and assets, continue maintenance, and keep this repository's provenance disclosure accurate. The current Flathub policy prohibits AI-generated/assisted manifest content and AI agents creating the Flathub submission PR or its messages. This work created no manifest, submission PR, or reviewer messages.
- The app ID/domain must be verified by the human owner through the current Flathub verification process before publication. No token has been fabricated or published.
- `docs/WEBSITE-INTEGRATION-DRAFT.md` contains factual copy and links to the current repository and release. It does not claim a website page exists; the production website was not changed.

## Assessment

- **Upstream technical readiness:** YES for the verified hardening branch. The changes still need owner review and integration into `main` before they describe the current public upstream state.
- **Ready for a human to begin packaging:** YES. The source, metadata, dependency provenance, and build notes are available for human review.
- **Ready for Flathub submission under current policy/history evidence:** NO. The project still needs organic real-world use and a sustained, demonstrable maintenance record, owner verification and review, a human-created offline package, and true sandbox/portal validation. These are distinct from the source-level checks above.

Re-read the current [Flathub requirements](https://docs.flathub.org/docs/for-app-authors/requirements), [MetaInfo quality guidelines](https://docs.flathub.org/docs/for-app-authors/metainfo-guidelines/quality-guidelines), [runtime policy](https://docs.flathub.org/docs/for-app-authors/runtimes), and [linter instructions](https://docs.flathub.org/docs/for-app-authors/linter) before any future submission.

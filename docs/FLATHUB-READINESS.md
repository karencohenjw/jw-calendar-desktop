# Flathub readiness review — 2026-10-02

This document records engineering findings for a future human-led package review. It is not a Flathub submission and contains no Flatpak manifest.

## Proposed identity and ownership verification

Proposed application ID: `com.jwcalendar.JWCalendar`. It uses the reverse-DNS form for the controlled `jwcalendar.com` domain. Before submission, the owner must verify the exact ID against current Flathub rules and use the Flathub Developer Portal to obtain a real verification token. Only then publish that token at `https://jwcalendar.com/.well-known/org.flathub.VerifiedApps.txt` (or use the currently supported DNS method). Never invent or commit a token.

Canonical homepage: `https://jwcalendar.com/`. The upstream repository is planned at `https://github.com/karencohenjw/jw-calendar-desktop`; verify those public links after the owner creates it.

The public upstream repository now exists at `https://github.com/karencohenjw/jw-calendar-desktop`. It currently has only the initial development history; the first commit is not evidence of sustained maintenance.

## Runtime and build shape

The UI needs a supported GNOME runtime that provides GTK 4, libadwaita, PyGObject, and Python 3.10 or newer. Select the runtime branch that is supported at the time of packaging. The application itself has no network or broad filesystem use. Its only user file access is the explicit save dialog for CSV and HTML export; GTK's file chooser portal should grant access to the chosen destination. Clipboard copy uses the desktop clipboard. The application has no reason to request network, home-directory, device, or session-bus permissions beyond the standard desktop integration supplied by the runtime.

The Python dependency is pinned to `jwcalendar-calendrical==0.1.0`. A future package must build from declared source archives with checksums and make all sources available before the offline build step. Do not use network access during the Flatpak build. Package the upstream launcher, scalable icon, and AppStream file from this repository. No final manifest has been authored here.

## Current policy and quality review

Flathub's current requirements call for sufficient functional scope, desktop integration, a sustained source history, real-world use, and ongoing maintenance. This upstream project begins with one initial development commit, so timing/policy readiness is not met today. The current generative-AI policy prohibits AI-generated or assisted content in the Flathub manifest and prohibits agents from opening or writing submission PRs and reviewer messages. This task has not created a manifest, submission branch, or PR. A human must perform all later Flathub packaging and submission work.

The GNOME runtime research snapshot is GNOME 50 as of 2026-10-02. Re-check the newest hosted runtime and SDK immediately before a future human packaging effort. The Flathub runtime must be current at submission time.

| Requirement | Status | Pass/Fail/N/A | Evidence | Required action |
|---|---|---|---|---|
| Supported runtime | Runtime family identified | Fail | GTK 4 / libadwaita UI; runtime branch intentionally not pinned | Choose a non-EOL GNOME runtime at submission time and build against it |
| Developer-managed project | Owner and official site identified | Fail | Karen Cohen and jwcalendar.com are documented; repository is new | Human owner review, sustained maintenance, and clear reporting contact |
| Icon | Original scalable vector plus 64/128/256 pixel PNG renders | Pass, pending Linux review | `data/icons/` | Review on light/dark desktops |
| Brand colors | Blue and teal documented | Pass, pending review | AppStream branding entries and SVG palette | Confirm brand alignment with project site |
| Screenshots | None supplied | Fail | No screenshots are fabricated | Capture genuine screenshots from the running Linux application after visual review |
| Name | JW Calendar | Pass, pending name review | AppStream, desktop entry, About window | Confirm no conflicting Flathub application ID/name at submission time |
| Summary | Concise, functional description | Pass, pending review | “Browse calendars, inspect dates, and calculate date differences” | Human editorial review |
| Description | Describes actual desktop behavior | Pass, pending review | AppStream description | Reconcile against shipped features before a stable release |
| Desktop integration | Desktop entry, app ID, scalable icon included | Pass, pending install verification | `data/com.jwcalendar.JWCalendar.desktop`; icon path | Verify installation and launching from a Flatpak build |
| Source and issue links | Public repository and issue tracker exist | Pass | AppStream and Snap metadata point to the public upstream repository | Re-check links during final public audit |
| Permissions | No broad permissions planned | Pass, pending sandbox test | No network/background access; user-chosen export and clipboard only | Validate GTK file chooser portal and clipboard in a sandbox |
| Release information | Development state only | Fail | New repository; no meaningful release history | Build a real history through human-maintained changes; tag a stable release only after validation |
| Verification | Domain method identified, no token | Fail until owner action | `jwcalendar.com` is canonical homepage | Obtain actual token in Developer Portal and publish it; never fabricate one |
| Offline operation | Core path and exports do not use network | Pass, pending runtime test | Source has no network client | Test with network unavailable in Linux environment |
| Accessibility and localization | Basic labels and selectable details; locale names | Fail / incomplete | Uses system month/day names; visual review not available here | Review keyboard focus, screen reader labels, RTL/layout, and translation readiness |
| AI provenance | Disclosed | Pass | `AI-ASSISTANCE.md` | Owner reviews content and follows current Flathub disclosure rules |

## Blocking work before a legitimate submission

1. Human owner review of all AI-assisted source, assets, and metadata; keep the provenance disclosure accurate.
2. Sustained development and meaningful maintenance history. Do not manufacture commits, tags, releases, or contributors.
3. Linux build and real UI validation, including screenshots, keyboard and accessibility review, file chooser portal behavior, and offline operation.
4. Genuine screenshots and a stable release with matching AppStream release metadata.
5. Select and verify a currently supported runtime, build every dependency offline from pinned sources, and verify the app ID and domain through Flathub's then-current process.
6. Confirm and publish a real private security contact route.
7. A human maintainer prepares any eventual Flathub packaging and all submission communication. This repository has no final Flatpak manifest or submission PR.

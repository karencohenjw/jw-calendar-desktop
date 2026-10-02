# Flathub readiness review — 2026-10-02

This document records engineering findings for a future human-led package review. It is not a Flathub submission and contains no Flatpak manifest.

## Proposed identity and ownership verification

Proposed application ID: `com.jwcalendar.JWCalendar`. It uses the reverse-DNS form for the controlled `jwcalendar.com` domain. Before submission, the owner must verify the exact ID against current Flathub rules and use the Flathub Developer Portal to obtain a real verification token. Only then publish that token at `https://jwcalendar.com/.well-known/org.flathub.VerifiedApps.txt` (or use the currently supported DNS method). Never invent or commit a token.

Canonical homepage: `https://jwcalendar.com/`. The public upstream repository and issue tracker are `https://github.com/karencohenjw/jw-calendar-desktop` and `https://github.com/karencohenjw/jw-calendar-desktop/issues`.

The public upstream repository now contains the application, tests, metadata, CI, Snap packaging, and human packaging guidance. Its commits were made during the initial project setup on 2026-10-02; that short history is not evidence of sustained maintenance or real-world use.

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
| Screenshots | Four genuine Linux captures and immutable URLs | Pass, pending human visual review | Ubuntu 24.04.5 LTS / GTK 4.14.5 / libadwaita 1.5.0 captures are public at screenshot commit `d45faa0fd23d75554c87e0e182bf757de6ca88a8`; AppStream URLs point directly to those raw images | Confirm visual fit and keep URLs pinned to the immutable source commit |
| Name | JW Calendar | Pass, pending name review | AppStream, desktop entry, About window | Confirm no conflicting Flathub application ID/name at submission time |
| Summary | Concise, functional description | Pass, pending review | “Browse calendars, inspect dates, and calculate date differences” | Human editorial review |
| Description | Describes actual desktop behavior | Pass, pending review | AppStream description | Reconcile against shipped features before a stable release |
| Desktop integration | Desktop entry, app ID, scalable icon included | Pass, pending install verification | `data/com.jwcalendar.JWCalendar.desktop`; icon path | Verify installation and launching from a Flatpak build |
| Source and issue links | Public repository and issue tracker exist | Pass | AppStream and Snap metadata point to the public upstream repository | Re-check links during final public audit |
| Permissions | No broad permissions planned; native chooser and both exports verified in Ubuntu GUI QA | Pass for unsandboxed GTK QA; Flatpak portal remains unverified | GUI QA run [#37052977644](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37052977644) saved and parsed a 42-cell CSV and a self-contained HTML calendar | Later validate file chooser portal behavior in an actual Flatpak sandbox |
| Release information | Public [`v0.1.1`](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.1) source release published | Pass for source release; Fail for sustained history | `v0.1.1` points to CI-verified commit `2015d95145c08a16e23ee1cb63639cadbd8a6691`; all project history is still from initial setup on 2026-10-02 | Continue human maintenance and use; do not treat same-day development as sustained history |
| Verification | Domain method identified, no token | Fail until owner action | `jwcalendar.com` is canonical homepage | Obtain actual token in Developer Portal and publish it; never fabricate one |
| Offline operation | Core path and exports do not use network | Pass, pending runtime test | Source has no network client | Test with network unavailable in Linux environment |
| Accessibility and localization | Basic labels and selectable details; locale names | Fail / incomplete | Uses system month/day names; visual review not available here | Review keyboard focus, screen reader labels, RTL/layout, and translation readiness |
| AI provenance | Disclosed | Pass | `AI-ASSISTANCE.md` | Owner reviews content and follows current Flathub disclosure rules |

## Blocking work before a legitimate submission

1. Human owner review of all AI-assisted source, assets, and metadata; keep the provenance disclosure accurate.
2. Sustained development and meaningful maintenance history beyond the initial same-day setup. Do not manufacture commits, tags, releases, or contributors.
3. Validate the GUI exports inside a real Flatpak portal sandbox; Ubuntu GTK QA run [#37052977644](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37052977644) verified both saved files and their contents.
4. Complete the human review of the published release metadata. The four genuine Linux screenshots are public at `d45faa0fd23d75554c87e0e182bf757de6ca88a8`, and AppStream image URLs are pinned to that commit.
5. Human visual review on Linux, keyboard and accessibility review, file chooser portal behavior, and offline operation. Automated GTK checks under Xvfb do not replace this review.
6. Select and verify a currently supported runtime, build every dependency offline from pinned sources, and verify the app ID and domain through Flathub's then-current process.
7. Confirm and publish a real private security contact route.
8. A human maintainer prepares any eventual Flathub packaging and all submission communication. This repository has no final Flatpak manifest or submission PR.

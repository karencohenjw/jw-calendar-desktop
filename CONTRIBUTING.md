# Contributing

Contributions should improve calendar correctness, accessibility, usability, or maintainability. Please describe the user-visible effect and include regression tests for calculation changes.

## Development setup

Use Python 3.10 or newer, GTK 4, PyGObject, and libadwaita 1.4 or newer. Install the project with `python -m pip install -e .` and run `python -m unittest discover -s tests -v`. UI changes should be checked on Linux with a real GTK display; automated headless checks are useful but do not replace a human accessibility and visual review.

## Calendar behavior

Gregorian and Julian civil calendars are distinct systems. Keep conversions based on the same absolute day, and keep Julian civil dates distinct from Julian Day Number. Document the supported date range and test leap years, century years, calendar boundaries, and ISO week-year boundaries when changing arithmetic or formatting.

## Changes and releases

Do not create artificial history, release tags, or download claims. Releases should represent tested, reviewable states. Check dependency updates and supported GTK/libadwaita versions before changing runtime assumptions.

## AI assistance

Disclose AI-generated or AI-assisted contributions in the pull request and update `AI-ASSISTANCE.md` as needed. Human maintainers remain responsible for correctness and provenance. Never add AI-generated Flathub manifests or submission text to this project.

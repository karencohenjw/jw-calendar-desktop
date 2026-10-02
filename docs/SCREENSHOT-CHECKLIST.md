# Linux screenshot evidence

The four PNGs in `data/screenshots/` were captured from the running application on Ubuntu 24.04.5 LTS in GitHub Actions. The runner used Python 3.12.3, GTK 4.14.5, libadwaita 1.5.0, Xvfb, and Openbox. Each image is an unedited 960 × 700 capture of the application window, with no desktop or editing interface.

The captures show:

1. Month view with 2027-01-01 selected and Gregorian, Julian, ISO week, ordinal, Julian Day Number, and leap-year details.
2. The full 2027 year overview, including all twelve month grids.
3. A Gregorian-to-Julian conversion and a 364-day date difference.
4. Help, appearance selection, keyboard hints, and project resource links.

The images were reviewed at full size for readable text, complete content, and layout. The year capture shows all twelve months without clipping. They currently exist in the local checkout only: the screenshot commit has not been pushed, so no public immutable image URLs are available. The local AppStream `v0.1.1` screenshot entries are a draft and must be replaced with raw URLs pinned to the actual public screenshot commit SHA after it is pushed. The public repository still reports source release `v0.1.0`; no `v0.1.1` release has been published.

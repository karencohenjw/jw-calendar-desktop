# Linux screenshot evidence

The four PNGs in `data/screenshots/` were captured from the running application on Ubuntu 24.04.5 LTS in GitHub Actions. The runner used Python 3.12.3, GTK 4.14.5, libadwaita 1.5.0, Xvfb, and Openbox. Each image is an unedited 1000 × 700 capture of the application window, within Flathub's 1000 × 700 limit.

The captures show:

1. Month view with 2027-01-01 selected and Gregorian, Julian, ISO week, ordinal, Julian Day Number, and leap-year details.
2. The complete 2027 year overview, including all twelve month grids without clipping.
3. A Gregorian-to-Julian conversion and a 364-day date difference.
4. Help, appearance selection, keyboard hints, and project resource links.

The first image is the general application overview. All four images were visually reviewed at full size for readable text, complete content, and layout. They are actual Linux application-window captures with no desktop background, editing interface, added text, or promotional overlay. Source application commit: `d9b00886ccb588a1f9e45cfb52cc389741e55d2e`. Screenshot QA: [Linux GUI QA run 37102312221](https://github.com/karencohenjw/jw-calendar-desktop/actions/runs/37102312221). The reviewed image assets are stored immutably at commit `ab5e7d41b9b25bcf50fbe0bfdf22a76f60e5e0ad`; AppStream image URLs point directly to those raw files. Current public stable is [`v0.1.1`](https://github.com/karencohenjw/jw-calendar-desktop/releases/tag/v0.1.1).

# Linux screenshot capture checklist

**Final store screenshots: HUMAN ACTION REQUIRED.** This checkout was developed and inspected on macOS. Do not use its window or a mockup as a Linux store screenshot.

On a supported Linux desktop, install the application from the source checkout and capture the actual application window at a comfortable readable size (at least 1280 × 800 pixels). Keep the desktop free of personal notifications and unrelated windows. Do not include terminal, browser, IDE, or editing UI. Use plausible dates and review every visible label before capture.

Required views:

1. Month page showing the full month grid and selected-date details.
2. Year page with all 12 month grids visible or clearly accessible by scrolling.
3. Gregorian/Julian conversion page showing a valid conversion and elapsed-days result.
4. Help page with appearance options and the project resource links.

Optional view:

5. The native save dialog opened from Export, only if the chooser does not expose personal paths or filenames.

Save original PNG screenshots in `data/screenshots/` and include them in the tagged release. Add AppStream screenshot URLs only after the images are public at an immutable release-tag URL and each URL has been opened and checked. A human should then verify the captures at Flathub's current screenshot size and quality requirements.

# Accessibility review

This records a real GTK/AT-SPI keyboard audit under Ubuntu/Xvfb. It is not a WCAG or full screen-reader certification.

## Keyboard behavior

- Tab and Shift+Tab use GTK's normal focus order; calendar date buttons remain individual focusable controls. Enter or Space activates buttons. The native save dialog supports Escape to cancel.
- In Month, Left/Right changes the month and Ctrl+Left/Ctrl+Right changes the year. Ctrl+1 through Ctrl+4 opens Month, Year, Convert, and Help.
- Enter in the date conversion field runs Convert. Enter in the end-date field runs Calculate.
- Copy, Export, About, previous month, and next month actions have explicit accessible names. Dropdowns and date inputs have names; date buttons announce weekday, full date, calendar, and ISO week. Selecting a date updates the accessible date details.
- Changing a selected date preserves keyboard focus on its date button.

## Verification boundaries

The CI AT-SPI audit inspects the live Linux application, visits all four pages using keyboard shortcuts, tabs to a date, activates it with Space, and checks accessible names and date details. No reliable spoken Orca session was available in this headless runner, so spoken output is not claimed. A human should review speech, contrast/high-contrast themes, text scaling, RTL, narrow-window layouts, and Wayland behavior on a regular Linux desktop. No formal WCAG conformance evaluation has been performed.

GTK 4.10's asynchronous `Gtk.FileDialog` returns a `GFile`; export writes through GIO. GTK's native file dialog uses `org.freedesktop.portal.FileChooser` when that portal is available. The separate non-Flatpak portal-readiness exercise is recorded in the workflow output and does not establish Flatpak sandbox behavior.

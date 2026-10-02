# Accessibility review

This is a code review and automated GTK/Xvfb smoke check, not a WCAG or assistive-technology certification.

## Verified

- Selected dates have a visible filled state and remain identified by the selected-date text panel; color is not the only indicator.
- Navigation and header actions use GTK controls. Icon-only actions have descriptive tooltips, and the date grid provides full-date and ISO-week tooltips.
- The Help page includes keyboard instructions, appearance settings, and resource links.
- The `Left` and `Right` keys changed the displayed month in the Ubuntu GUI workflow. GTK/Xvfb integration checks also exercised the clipboard API.
- Default GTK/libadwaita light styling rendered legible labels and controls in the reviewed Linux screenshots.

## Not yet verified

- Tab and Shift+Tab focus order, Enter/Space activation, and keyboard operation of the native save dialog have not been systematically audited.
- No Orca or other screen reader review was performed. Calendar cells expose their day number as the accessible label; spoken date context should be checked.
- Dark and high-contrast themes, text scaling, RTL layout, narrow-window layouts, and a Wayland desktop session need additional review.
- The save dialog and clipboard were exercised in Ubuntu's Xvfb session, but a real Flatpak portal sandbox was not built or tested.
- No formal WCAG conformance evaluation has been performed.

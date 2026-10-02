# Accessibility review

This is a code-level review of the initial Linux interface, not a claim of WCAG or assistive-technology certification.

## Current support

- All calendar and form controls are GTK widgets and can be reached by keyboard focus traversal.
- Previous/next month and year navigation supports the left/right arrow keys when focus is outside an entry or selector.
- The Today, copy, export, and navigation icon buttons have visible text or tooltips describing their actions.
- Calendar day buttons show the full civil date and ISO week in their tooltip; selected dates also appear in a text details area.
- Date details and conversion results are selectable text, so users can copy them without relying on color.
- Theme choice follows the desktop by default and has light and dark options. Layout colors are supplied by GTK/libadwaita themes rather than hard-coded meaning colors.
- The month and year pages use scrollable/adaptive containers; the window minimum is 600 by 460 logical pixels and the year page scrolls vertically.

## Known review work

- A Linux user should test keyboard-only operation and focus order with GTK Inspector and a screen reader such as Orca.
- Calendar buttons currently present their day number as the visible label; date tooltips help disambiguate the full date, but a spoken-label review is still needed.
- Check text scaling, high-contrast themes, RTL locales, and very narrow windows on supported desktop environments.
- The desktop file chooser and clipboard should be tested in real Wayland/X11 sessions and under a sandbox portal. CI smoke tests do not prove portal behavior.
- No formal WCAG conformance evaluation has been performed.

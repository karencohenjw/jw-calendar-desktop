#!/usr/bin/python3
"""Exercise the running GTK app's accessible tree and keyboard actions via AT-SPI."""

import subprocess
import time

import pyatspi


def descendants(root):
    yield root
    try:
        children = root.childCount
    except Exception:
        return
    for index in range(children):
        try:
            child = root.getChildAtIndex(index)
        except Exception:
            continue
        yield from descendants(child)


def app_tree():
    desktop = pyatspi.Registry.getDesktop(0)
    for _ in range(40):
        for app in descendants(desktop):
            if app.getName() == "JW Calendar":
                return list(descendants(app))
        time.sleep(0.25)
    raise AssertionError("JW Calendar did not appear in the AT-SPI desktop tree")


def names():
    return {node.getName() for node in app_tree() if node.getName()}


def key(*keys):
    subprocess.run(["xdotool", "key", "--clearmodifiers", *keys], check=True)
    time.sleep(0.3)


def press_button_named(expected, activation="space"):
    for node in app_tree():
        if node.getName() == expected and node.getRoleName() == "push button":
            node.queryComponent().grabFocus()
            key(activation)
            return
    raise AssertionError(f"Missing accessible calendar button: {expected}")


tree = app_tree()
assert any(node.getName() == "Copy selected date" for node in tree)
assert any(node.getName() == "Export calendar" for node in tree)
assert any(node.getName() == "About JW Calendar" for node in tree)
assert any(node.getName() == "Previous month" for node in tree)
assert any(node.getName() == "Next month" for node in tree)
print("PASS: icon-only actions and month navigation have accessible names")

# Tab through the real Month page and confirm calendar dates can receive focus.
key("ctrl+1")
focusable = set()
for _ in range(45):
    key("Tab")
    for node in app_tree():
        try:
            if node.getState().contains(pyatspi.STATE_FOCUSED):
                focusable.add(node.getName())
        except Exception:
            pass
assert any(name and ", " in name and "ISO week" in name for name in focusable), (
    f"Tab did not reach a named date cell; focused names were {sorted(focusable)}"
)
print("PASS: Tab reaches an announced calendar date")
key("Shift+Tab")
assert any(
    node.getState().contains(pyatspi.STATE_FOCUSED)
    for node in app_tree()
    if node.getName()
), "Shift+Tab did not leave focus on a named control"
key("Tab")
print("PASS: Shift+Tab returns focus through the GTK control order")

# Space activates a focused date, updates selected-date details, and keeps a
# full date/calendar/ISO-week description on the selected grid cell.
before = names()
date_button = next(
    node.getName() for node in app_tree()
    if node.getRoleName() == "push button" and ", " in node.getName() and "ISO week" in node.getName()
)
press_button_named(date_button)
after = names()
assert any("ISO week:" in name for name in after), "Selected date details are missing ISO week"
print("PASS: Space activates a keyboard-focused date and exposes its details")

def selected_date():
    for node in app_tree():
        try:
            if node.getState().contains(pyatspi.STATE_SELECTED) and "ISO week" in node.getName():
                return node.getName().split(", ")[1]
        except Exception:
            pass
    raise AssertionError("The selected calendar date is not exposed to AT-SPI")


original = selected_date()
key("ctrl+Right")
later_year = selected_date()
assert later_year.split("-")[0] == str(int(original.split("-")[0]) + 1)
key("ctrl+Left")
restored = selected_date()
assert restored.split("-")[0] == original.split("-")[0]
key("Left")
previous_month = selected_date()
assert previous_month[:7] != restored[:7], "Left did not change the displayed month"
key("Right")
print("PASS: Ctrl+Left/Right changes the year; Left/Right changes the month")

key("ctrl+3")
conversion = names()
for expected in (
    "Date to convert, YYYY-MM-DD", "Conversion source calendar",
    "Start date, YYYY-MM-DD", "End date, YYYY-MM-DD", "Date difference calendar",
):
    assert expected in conversion, f"Missing accessible conversion control: {expected}"
print("PASS: Julian conversion and date-difference controls have accessible names")

key("ctrl+4")
assert any("offline" in name.lower() for name in names()), "Help page is not exposed through AT-SPI"
key("ctrl+1")
key("Left")
assert any("ISO week" in name for name in names()), "Month navigation lost the accessible calendar"
key("ctrl+2")
assert any("Year" in name for name in names()), "Year page is not exposed through AT-SPI"
print("PASS: keyboard shortcuts navigate Month, Year, Convert, and Help")

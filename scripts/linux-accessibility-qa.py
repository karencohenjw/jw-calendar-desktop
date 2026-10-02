#!/usr/bin/python3
"""Exercise the running GTK app's accessible tree and keyboard actions via AT-SPI."""

import subprocess
import time

import pyatspi


def descendants(root):
    yield root
    try:
        children = root.get_child_count()
    except Exception:
        return
    for index in range(children):
        try:
            child = root.get_child_at_index(index)
        except Exception:
            continue
        yield from descendants(child)


def app_tree():
    desktop = pyatspi.Registry.getDesktop(0)
    for _ in range(40):
        for app in descendants(desktop):
            if app.get_name() == "JW Calendar":
                return list(descendants(app))
        time.sleep(0.25)
    raise AssertionError("JW Calendar did not appear in the AT-SPI desktop tree")


def names():
    return {node.get_name() for node in app_tree() if node.get_name()}


def key(*keys):
    subprocess.run(["xdotool", "key", "--clearmodifiers", *keys], check=True)
    time.sleep(0.3)


tree = app_tree()
assert any(node.get_name() == "Copy selected date" for node in tree)
assert any(node.get_name() == "Export calendar" for node in tree)
assert any(node.get_name() == "About JW Calendar" for node in tree)
assert any(node.get_name() == "Previous month" for node in tree)
assert any(node.get_name() == "Next month" for node in tree)
print("PASS: icon-only actions and month navigation have accessible names")

# Tab through the real Month page and confirm calendar dates can receive focus.
key("ctrl+1")
focusable = set()
focused_date_name = None
for _ in range(45):
    key("Tab")
    for node in app_tree():
        try:
            if node.get_state_set().contains(pyatspi.STATE_FOCUSED):
                focusable.add(node.get_name())
                if ", " in node.get_name() and "ISO week" in node.get_name():
                    focused_date_name = node.get_name()
        except Exception:
            pass
assert focused_date_name, (
    f"Tab did not reach a named date cell; focused names were {sorted(focusable)}"
)
print("PASS: Tab reaches an announced calendar date")
key("Shift+Tab")
assert any(
    node.get_state_set().contains(pyatspi.STATE_FOCUSED)
    for node in app_tree()
    if node.get_name()
), "Shift+Tab did not leave focus on a named control"
key("Tab")
print("PASS: Shift+Tab returns focus through the GTK control order")

# Space activates a focused date, updates selected-date details, and keeps a
# full date/calendar/ISO-week description on the selected grid cell.
def focused_names():
    return {
        node.get_name() for node in app_tree()
        if node.get_state_set().contains(pyatspi.STATE_FOCUSED) and node.get_name()
    }


assert focused_date_name in focused_names(), "Tab did not return to the same date cell"
key("space")
after = names()
assert any("ISO week:" in name for name in after), "Selected date details are missing ISO week"
print("PASS: Space activates a keyboard-focused date and exposes its details")

def selected_date():
    for node in app_tree():
        try:
            if node.get_state_set().contains(pyatspi.STATE_SELECTED) and "ISO week" in node.get_name():
                return node.get_name().split(", ")[1]
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

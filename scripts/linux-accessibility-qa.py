#!/usr/bin/python3
"""Exercise the running GTK app's accessible tree and keyboard actions via AT-SPI."""

import re
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


def descriptions():
    return {node.get_description() for node in app_tree() if node.get_description()}


def key(*keys):
    subprocess.run(["xdotool", "key", "--clearmodifiers", *keys], check=True)
    time.sleep(0.3)


tree = app_tree()
date_controls = [
    (node.get_role_name(), node.get_name(), node.get_description())
    for node in tree
    if "ISO week" in (node.get_description() or "")
]
print(f"AT-SPI date-related controls: {date_controls[:6]}")
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
                description = node.get_description() or ""
                if node.get_role_name() == "push button" and "ISO week" in description:
                    focused_date_name = description
                    break
        except Exception:
            pass
    if focused_date_name:
        break
assert focused_date_name, (
    f"Tab did not reach a named date cell; focused names were {sorted(focusable)}; "
    f"date controls were {date_controls[:12]}"
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

# Enter activates a focused date and updates selected-date details. The
# focused cell has already been checked for its full date and ISO-week label.


def focused_names():
    return {
        node.get_name() for node in app_tree()
        if node.get_state_set().contains(pyatspi.STATE_FOCUSED) and node.get_name()
    }


assert any(
    node.get_state_set().contains(pyatspi.STATE_FOCUSED)
    and node.get_role_name() == "push button"
    and node.get_description() == focused_date_name
    for node in app_tree()
), "Tab did not return to the same date cell"
focused_parts = focused_date_name.split(", ")
focused_date = focused_parts[2] if focused_parts[0] == "Selected date" else focused_parts[1]
key("Return")
def detail_date():
    for name in names():
        match = re.search(r"Gregorian: (\d{4}-\d{2}-\d{2})", name)
        if match:
            return match.group(1)
    raise AssertionError("Selected-date details are missing the Gregorian date")

selected_after_activation = detail_date()
assert selected_after_activation == focused_date, (
    f"Enter did not select the focused date: focused={focused_date}, selected={selected_after_activation}"
)
assert any("ISO week:" in name for name in names()), "Selected date details are missing ISO week"
print("PASS: Enter activates a keyboard-focused date and updates its accessible details")


original = detail_date()
key("ctrl+Right")
later_year = detail_date()
assert later_year.split("-")[0] == str(int(original.split("-")[0]) + 1)
key("ctrl+Left")
restored = detail_date()
assert restored.split("-")[0] == original.split("-")[0]
key("Left")
previous_month = detail_date()
assert previous_month[:7] != restored[:7], "Left did not change the displayed month"
key("Right")
print("PASS: Ctrl+Left/Right changes the year; Left/Right changes the month")

key("ctrl+3")
conversion = names() | descriptions()
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

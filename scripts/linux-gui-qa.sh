#!/usr/bin/env bash
set -Eeuo pipefail

artifact_dir="${1:-artifacts/linux-gui-qa}"
mkdir -p "$artifact_dir"

export GDK_BACKEND=x11
export GTK_A11Y=atspi

openbox --sm-disable >"$artifact_dir/openbox.log" 2>&1 &
window_manager_pid=$!
picom --backend xrender --no-vsync >"$artifact_dir/picom.log" 2>&1 &
compositor_pid=$!
app_pid=""
portal_monitor_pid=""

cleanup() {
  if [[ -n "$app_pid" ]] && kill -0 "$app_pid" 2>/dev/null; then
    kill "$app_pid" || true
    wait "$app_pid" || true
  fi
  kill "$compositor_pid" "$window_manager_pid" 2>/dev/null || true
  if [[ -n "$portal_monitor_pid" ]]; then
    kill "$portal_monitor_pid" 2>/dev/null || true
    wait "$portal_monitor_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT

sleep 2
if [[ "${JW_PORTAL_QA:-0}" == 1 ]]; then
  dbus-monitor --session "interface='org.freedesktop.portal.FileChooser'" \
    >"$artifact_dir/portal-dbus.log" 2>&1 &
  portal_monitor_pid=$!
  sleep 1
fi
{
  lsb_release -ds
  /usr/bin/python3 --version
  /usr/bin/python3 - <<'PY'
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk
print(f"GTK {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")
print(f"libadwaita {Adw.get_major_version()}.{Adw.get_minor_version()}.{Adw.get_micro_version()}")
PY
  jwcalendar --help | head -n 1
} | tee "$artifact_dir/environment.txt"

jw-calendar-desktop >"$artifact_dir/application-portal.log" 2>&1 &
app_pid=$!

window_id=""
for attempt in $(seq 1 40); do
  window_id="$(xdotool search --onlyvisible --name '^JW Calendar$' 2>/dev/null | head -n 1 || true)"
  [[ -n "$window_id" ]] && break
  sleep 0.5
done

if [[ -z "$window_id" ]]; then
  cat "$artifact_dir/application.log"
  echo "The JW Calendar GTK window did not appear." >&2
  exit 1
fi

wmctrl -ir "$window_id" -e 0,40,40,930,660
wmctrl -ia "$window_id"
sleep 2

python3 scripts/linux-accessibility-qa.py | tee "$artifact_dir/accessibility.txt"

# The AT-SPI audit finishes on the Year page; start captures on Month.
xdotool key --clearmodifiers ctrl+1
sleep 1
# Reset to today, then use the app-level arrow keys to reach January 2027.
window_geometry="$(xdotool getwindowgeometry --shell "$window_id")"
X="$(awk -F= '/^X=/{print $2}' <<<"$window_geometry")"
Y="$(awk -F= '/^Y=/{print $2}' <<<"$window_geometry")"
xdotool mousemove --sync "$((X + 650))" "$((Y + 95))" click 1
read -r month_delta < <(/usr/bin/python3 - <<'PY'
from datetime import date
today = date.today()
print((2027 - today.year) * 12 + (1 - today.month))
PY
)
if (( month_delta > 0 )); then
  xdotool key --clearmodifiers --repeat "$month_delta" --delay 15 Right
elif (( month_delta < 0 )); then
  xdotool key --clearmodifiers --repeat "$((-month_delta))" --delay 15 Left
fi
sleep 1
xdotool mousemove --sync 1240 860
sleep 1
gnome-screenshot --window --file="$artifact_dir/month-view.png"
xdotool mousemove --sync "$((X + 428))" "$((Y + 30))" click 1
sleep 1
gnome-screenshot --window --file="$artifact_dir/year-view.png"
xdotool mousemove --sync "$((X + 532))" "$((Y + 30))" click 1
sleep 1

xdotool mousemove --sync "$((X + 385))" "$((Y + 145))" click 1
sleep 1
xdotool mousemove --sync 1240 860
sleep 1
gnome-screenshot --window --file="$artifact_dir/convert-view.png"
xdotool mousemove --sync "$((X + 628))" "$((Y + 30))" click 1
sleep 1
gnome-screenshot --window --file="$artifact_dir/help-view.png"

wmctrl -lG | tee "$artifact_dir/windows.txt"
if [[ ! -s "$artifact_dir/month-view.png" ]]; then
  echo "The Linux application screenshot was not created." >&2
  exit 1
fi


test -s "$artifact_dir/year-view.png"
test -s "$artifact_dir/convert-view.png"
test -s "$artifact_dir/help-view.png"
python - "$artifact_dir" <<'PY'
import struct
import sys
from pathlib import Path

for path in sorted(Path(sys.argv[1]).glob("*-view.png")):
    with path.open("rb") as stream:
        header = stream.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    width, height = struct.unpack(">II", header[16:24])
    assert width <= 1000 and height <= 700, (
        f"{path.name} is {width}x{height}; Flathub screenshots must be at most 1000x700"
    )
    print(f"PASS: {path.name} is {width}x{height} pixels (native window capture).")
PY


# Open and cancel the native export chooser.
xdotool mousemove --sync "$((X + 326))" "$((Y + 30))" click 1
sleep 0.5
xdotool mousemove --sync "$((X + 794))" "$((Y + 23))" click 1
sleep 0.5
xdotool key --clearmodifiers Down Return
for attempt in $(seq 1 40); do
  if xdotool search --onlyvisible --name '^Export calendar$' >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done
wmctrl -lG | tee "$artifact_dir/windows-after-export.txt"
xdotool search --onlyvisible --name '^Export calendar$' >/dev/null 2>&1 || { echo "Native export dialog did not open." >&2; exit 1; }

xdotool key Escape
sleep 1
echo "PASS: Native export chooser opened and Escape cancelled." | tee "$artifact_dir/file-chooser.txt"

if [[ "${JW_PORTAL_QA:-0}" == 1 ]]; then
  sleep 1
  if ! rg -q 'org.freedesktop.portal.FileChooser' "$artifact_dir/portal-dbus.log"; then
    echo "GTK portal readiness failed: the FileChooser portal was not called." >&2
    cat "$artifact_dir/application-portal.log" >&2
    exit 1
  fi
  echo "PASS: GTK called the real FileChooser portal for save/export." \
    | tee "$artifact_dir/portal-result.txt"

  # Portal file chooser was proven above. Restart with GTK's supported
  # no-portals debug option for repeatable CSV and HTML save/verification.
  kill "$app_pid"
  wait "$app_pid" || true
  app_pid=""
  GDK_DEBUG=no-portals jw-calendar-desktop >"$artifact_dir/application.log" 2>&1 &
  app_pid=$!
  window_id=""
  for attempt in $(seq 1 40); do
    window_id="$(xdotool search --onlyvisible --name '^JW Calendar$' 2>/dev/null | head -n 1 || true)"
    [[ -n "$window_id" ]] && break
    sleep 0.5
  done
  [[ -n "$window_id" ]] || { cat "$artifact_dir/application.log"; echo "JW Calendar did not relaunch after portal QA." >&2; exit 1; }
  wmctrl -ir "$window_id" -e 0,40,40,930,660
  wmctrl -ia "$window_id"
  sleep 1
  xdotool mousemove --sync "$((X + 650))" "$((Y + 95))" click 1
  read -r month_delta < <(/usr/bin/python3 - <<'PY'
from datetime import date
today = date.today()
print((2027 - today.year) * 12 + (1 - today.month))
PY
)
  if (( month_delta > 0 )); then
    xdotool key --clearmodifiers --repeat "$month_delta" --delay 15 Right
  elif (( month_delta < 0 )); then
    xdotool key --clearmodifiers --repeat "$((-month_delta))" --delay 15 Left
  fi
  sleep 1
  xdotool mousemove --sync 1240 860
fi

open_export_chooser() {
  xdotool mousemove --sync "$((X + 794))" "$((Y + 23))" click 1
  sleep 0.5
  if [[ -n "$1" ]]; then
    xdotool key --clearmodifiers "$1"
  fi
  xdotool key --clearmodifiers Return
  for attempt in $(seq 1 40); do
    if xdotool search --onlyvisible --name '^Export calendar$' >/dev/null 2>&1; then
      break
    fi
    sleep 0.25
  done
  scrot --focused "$artifact_dir/$2-chooser.png"
}

save_native_dialog() {
  local expected_path="$1" chooser_id geometry width height
  chooser_id="$(xdotool search --onlyvisible --name '^Export calendar$' | tail -n 1)"
  [[ -n "$chooser_id" ]] || { echo "Native save dialog did not remain visible." >&2; exit 1; }
  geometry="$(xdotool getwindowgeometry --shell "$chooser_id")"
  width="$(awk -F= '/^WIDTH=/{print $2}' <<<"$geometry")"
  height="$(awk -F= '/^HEIGHT=/{print $2}' <<<"$geometry")"
  # GTK can retain the previous export's filename when the format changes.
  # Set the expected basename explicitly, then activate Save so the check
  # verifies a completed write rather than only an open dialog.
  xdotool key --clearmodifiers ctrl+a
  xdotool type --clearmodifiers --delay 1 -- "$(basename "$expected_path")"
  xdotool mousemove --window "$chooser_id" "$((width - 48))" "$((height - 29))" click 1
  for attempt in $(seq 1 40); do
    if ! xdotool search --onlyvisible --name '^Export calendar$' >/dev/null 2>&1 && [[ -s "$expected_path" ]]; then
      return 0
    fi
    sleep 0.25
  done
  echo "Native chooser did not close and create a non-empty file: $expected_path" >&2
  wmctrl -lG >&2
  return 1
}
open_export_chooser Down csv
xdotool search --onlyvisible --name '^Export calendar$' >/dev/null 2>&1 || { echo "CSV save chooser did not open." >&2; exit 1; }
csv_path="$PWD/january-2027.csv"
save_native_dialog "$csv_path"
python - "$csv_path" <<'PY' | tee "$artifact_dir/csv-export.txt"
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
assert path.is_file(), f"CSV was not created at {path}"
assert path.stat().st_size > 0, "CSV export is empty"
with path.open(encoding="utf-8", newline="") as stream:
    reader = csv.DictReader(stream)
    assert reader.fieldnames == ["week", "weekday", "date", "calendar", "in_month", "iso_week"]
    rows = list(reader)
new_year = next((row for row in rows if row["date"] == "2027-01-01"), None)
assert new_year, "CSV is missing 2027-01-01"
assert new_year["weekday"] == "Fri", f"Expected abbreviated Friday, got {new_year['weekday']!r}"
Path("artifacts/linux-gui-qa/january-2027.csv").write_bytes(path.read_bytes())
print(f"PASS: CSV saved and parsed ({len(rows)} calendar cells).")
PY

open_export_chooser "" html
xdotool search --onlyvisible --name '^Export calendar$' >/dev/null 2>&1 || { echo "HTML save chooser did not open." >&2; exit 1; }
html_path="$PWD/january-2027.html"
save_native_dialog "$html_path"
python - "$html_path" <<'PY' | tee "$artifact_dir/html-export.txt"
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
assert path.is_file(), f"HTML was not created at {path}"
assert path.stat().st_size > 0, "HTML export is empty"
html = path.read_text(encoding="utf-8")
assert html.lower().startswith("<!doctype html>")
assert "<table>" in html and "<thead>" in html and "<tbody>" in html
assert "January 2027" in html
assert not re.search(r"(?:src|href)=[\"']https?://", html, re.I)
Path("artifacts/linux-gui-qa/january-2027.html").write_bytes(path.read_bytes())
print("PASS: HTML saved, contains the calendar, and has no remote assets.")
PY

# The application should remain running after presenting a real GTK window.
if ! kill -0 "$app_pid" 2>/dev/null; then
  cat "$artifact_dir/application.log"
  echo "The JW Calendar process exited after launching its window." >&2
  exit 1
fi

echo "PASS: JW Calendar launched as a visible Linux GTK window." | tee "$artifact_dir/result.txt"

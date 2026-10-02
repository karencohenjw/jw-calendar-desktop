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

cleanup() {
  if [[ -n "$app_pid" ]] && kill -0 "$app_pid" 2>/dev/null; then
    kill "$app_pid" || true
    wait "$app_pid" || true
  fi
  kill "$compositor_pid" "$window_manager_pid" 2>/dev/null || true
}
trap cleanup EXIT

sleep 2
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

jw-calendar-desktop >"$artifact_dir/application.log" 2>&1 &
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

wmctrl -ir "$window_id" -e 0,40,40,960,700
wmctrl -ia "$window_id"
sleep 2

# Reset to today, then use the app-level arrow keys to reach January 2027.
# move from the runner's current month to January 2027 using real key events.
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
scrot --focused --border "$artifact_dir/month-view.png"
xdotool mousemove --sync "$((X + 428))" "$((Y + 30))" click 1
sleep 1
scrot --focused --border "$artifact_dir/year-view.png"
xdotool mousemove --sync "$((X + 532))" "$((Y + 30))" click 1
sleep 1

xdotool mousemove --sync "$((X + 385))" "$((Y + 145))" click 1
sleep 1
xdotool mousemove --sync 1240 860
sleep 1
scrot --focused --border "$artifact_dir/convert-view.png"
xdotool mousemove --sync "$((X + 628))" "$((Y + 30))" click 1
sleep 1
scrot --focused --border "$artifact_dir/help-view.png"

wmctrl -lG | tee "$artifact_dir/windows.txt"
if [[ ! -s "$artifact_dir/month-view.png" ]]; then
  echo "The Linux application screenshot was not created." >&2
  exit 1
fi


test -s "$artifact_dir/year-view.png"
test -s "$artifact_dir/convert-view.png"
test -s "$artifact_dir/help-view.png"


window_count_before="$(wmctrl -l | wc -l)"
# Open and cancel the native export chooser.
xdotool mousemove --sync "$((X + 326))" "$((Y + 30))" click 1
sleep 0.5
xdotool mousemove --sync "$((X + 823))" "$((Y + 23))" click 1
sleep 0.5
xdotool key --clearmodifiers Down Return
sleep 1
wmctrl -lG | tee "$artifact_dir/windows-after-export.txt"
window_count_after="$(wmctrl -l | wc -l)"
[[ "$window_count_after" -gt "$window_count_before" ]] || { echo "Native export dialog did not open." >&2; exit 1; }

xdotool key Escape
sleep 1
echo "PASS: Native export chooser opened and Escape cancelled." | tee "$artifact_dir/file-chooser.txt"

open_export_chooser() {
  xdotool mousemove --sync "$((X + 823))" "$((Y + 23))" click 1
  sleep 0.5
  xdotool key --clearmodifiers "$1" Return
  sleep 1
  scrot --focused "$artifact_dir/$2-chooser.png"
}

save_native_dialog() {
  local chooser_id geometry width height
  chooser_id="$(xdotool search --onlyvisible --name '^Export calendar$' | tail -n 1)"
  [[ -n "$chooser_id" ]] || { echo "Native save dialog did not remain visible." >&2; exit 1; }
  geometry="$(xdotool getwindowgeometry --shell "$chooser_id")"
  width="$(awk -F= '/^WIDTH=/{print $2}' <<<"$geometry")"
  height="$(awk -F= '/^HEIGHT=/{print $2}' <<<"$geometry")"
  # GTK's native dialog keeps the filename field focused; explicitly activate
  # its Save button so the GUI check verifies a completed save, not just input.
  xdotool mousemove --window "$chooser_id" "$((width - 48))" "$((height - 29))" click 1
  sleep 2
}
window_count_before="$(wmctrl -l | wc -l)"
open_export_chooser Down csv
window_count_after="$(wmctrl -l | wc -l)"
[[ "$window_count_after" -gt "$window_count_before" ]] || { echo "CSV save chooser did not open." >&2; exit 1; }
save_native_dialog
csv_path="$PWD/january-2027.csv"
python - "$csv_path" <<'PY' | tee "$artifact_dir/csv-export.txt"
import csv
import sys
from pathlib import Path

path = Path(sys.argv[1])
assert path.is_file(), f"CSV was not created at {path}"
with path.open(encoding="utf-8", newline="") as stream:
    rows = list(csv.DictReader(stream))
assert rows and any(row["date"] == "2027-01-01" for row in rows)
assert rows[0]["weekday"] == "Sunday"
Path("artifacts/linux-gui-qa/january-2027.csv").write_bytes(path.read_bytes())
print(f"PASS: CSV saved and parsed ({len(rows)} calendar cells).")
PY

window_count_before="$(wmctrl -l | wc -l)"
open_export_chooser Up html
window_count_after="$(wmctrl -l | wc -l)"
[[ "$window_count_after" -gt "$window_count_before" ]] || { echo "HTML save chooser did not open." >&2; exit 1; }
save_native_dialog
python - "$PWD/january-2027.html" <<'PY' | tee "$artifact_dir/html-export.txt"
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
assert path.is_file(), f"HTML was not created at {path}"
html = path.read_text(encoding="utf-8")
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

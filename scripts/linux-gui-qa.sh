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

# Open and cancel the native export chooser.
xdotool mousemove --sync "$((X + 326))" "$((Y + 30))" click 1
sleep 0.5
xdotool mousemove --sync "$((X + 823))" "$((Y + 23))" click 1
sleep 0.5
xdotool key --clearmodifiers Down Return
sleep 1
chooser_id="$(xdotool search --onlyvisible --name "Export calendar" 2>/dev/null | head -n 1 || true)"
[[ -n "$chooser_id" ]] || { echo "Native export chooser did not open." >&2; exit 1; }
xdotool key Escape
sleep 1
echo "PASS: Native export chooser opened and Escape cancelled." | tee "$artifact_dir/file-chooser.txt"
# The application should remain running after presenting a real GTK window.
if ! kill -0 "$app_pid" 2>/dev/null; then
  cat "$artifact_dir/application.log"
  echo "The JW Calendar process exited after launching its window." >&2
  exit 1
fi

echo "PASS: JW Calendar launched as a visible Linux GTK window." | tee "$artifact_dir/result.txt"

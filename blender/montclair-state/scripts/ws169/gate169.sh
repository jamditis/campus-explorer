cd /workspace/nj-scenes/montclair-state
# wait for MemAvailable >= 7500 MB, give up at 19:04 (next hourly session starts ~19:17; one Blender at a time)
until [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 7500 ]; do
  [ $(date +%H%M) -ge 1904 ] && { echo "$(date +%T) GATE TIMEOUT avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }
  sleep 10; done
bash scripts/ws169/loop169.sh
[ -e montclair_state_ws169a.blend ] && echo "$(date +%T) FIXDONE"

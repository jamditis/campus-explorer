#!/bin/bash
# run blender render with a MemAvailable watchdog (kill if < 700 MB)
"$@" & P=$!
while kill -0 $P 2>/dev/null; do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); if [ "$a" -lt ${WD_MIN:-700} ]; then echo "WATCHDOG KILL avail=$a"; pkill -9 -P $P; kill -9 $P; fi; sleep 0.3; done
wait $P

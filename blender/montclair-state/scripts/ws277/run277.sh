#!/bin/bash
# ws277: f277a on main as a merge208 CHAIN -> ws277a.blend.
# Run it in its own memory unit on Legion:
#   systemd-run --unit=cemain-job-$(date +%s) -p MemoryMax=10G -p Nice=10 --wait --collect --pipe bash scripts/ws277/run277.sh
# Exits non-zero unless Blender exits 0 and merge208 prints SAVED; the output file is removed first, so a failed run never
# leaves an older file under the same name.
set -o pipefail
cd /workspace/nj-scenes/montclair-state
CHAIN=${CHAIN:-ws277/f277a.py}; OUTN=${OUTN:-ws277a.blend}; LOG=$(mktemp)
rm -f "$PWD/$OUTN"
CHAIN="$CHAIN" INF=${INF:-$PWD/montclair_state.blend} OUT=$PWD/$OUTN WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python-exit-code 1 --python scripts/ws208/merge208.py > "$LOG" 2>&1
RC=$?
grep -E "F277|OFF208|POKE208|SAVED|MEM208 VmHWM|rror|Trace|WATCH|refused" "$LOG"
grep -q '^SAVED' "$LOG" && [ $RC -eq 0 ] && [ -s "$PWD/$OUTN" ] || { echo "RUN277 FAILED rc=$RC (log $LOG)"; exit 1; }
rm -f "$LOG"

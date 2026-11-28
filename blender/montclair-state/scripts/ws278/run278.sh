#!/bin/bash
# ws278: pre-release check (ws267/m5wrap267 in the merge208 loader, no save: it ends with os._exit(0) after M5C264 END), then the
# release strip. Stops before the strip unless the check exits 0, prints M5C264 END and was not watchdog-killed.
# Run in a 10G unit on Legion: systemd-run --unit=cemain-job-$(date +%s) -p MemoryMax=10G --wait --collect --pipe bash run278.sh
set -o pipefail
cd /workspace/nj-scenes/montclair-state
LOG=$(mktemp)
CHAIN=ws267/m5wrap267.py INF=$PWD/montclair_state.blend OUT=/tmp/m5_nosave.blend bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python-exit-code 1 --python scripts/ws208/merge208.py > "$LOG" 2>&1
RC=$?
grep -E "M5C264|WATCHDOG|rror|Trace" "$LOG" | cut -c1-300
rm -f /tmp/m5_nosave.blend
[ $RC -eq 0 ] && grep -q "^M5C264 END" "$LOG" && ! grep -q "WATCHDOG KILL" "$LOG" || { echo "M5CHECK FAILED rc=$RC (log $LOG)"; exit 1; }
rm -f "$LOG"
GATE=3300 bash scripts/ws278/strip278.sh; echo "RC $?"

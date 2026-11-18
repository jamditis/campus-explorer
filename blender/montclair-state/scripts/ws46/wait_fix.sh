#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 50); do
  a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
  if [ "$a" -gt 5200 ]; then
    echo "$(date +%T) avail $a MB — applying"
    cp montclair_state.blend montclair_state_pre_20261111ws46.blend
    printf '#!/bin/bash\ncp /workspace/nj-scenes/montclair-state/montclair_state_pre_20261111ws46.blend /workspace/nj-scenes/montclair-state/montclair_state.blend\n' > scripts/ws46/ws46_revert_all.sh; chmod +x scripts/ws46/ws46_revert_all.sh
    WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws46/fix_qi.py 2>&1 | grep -E "F46|rror|WATCHDOG|Saved"
    sha256sum montclair_state.blend; exit 0
  fi
  sleep 30
done
echo "$(date +%T) memory stayed pinned (last $a MB) — not applied"

#!/bin/bash
# wait for MemAvailable >= NEED until DEADLINE (epoch s); exit without starting Blender if not reached
cd /workspace/nj-scenes/montclair-state
while [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -lt ${NEED:-6500} ]; do
  [ $(date +%s) -ge $DEADLINE ] && { echo "$(date +%T) NOGO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"; exit 3; }
  sleep 3; done
echo "$(date +%T) GO avail=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
OUT=/workspace/nj-scenes/montclair-state/montclair_state_ws143a.blend WD_MIN=1200 bash scripts/ws33/wd.sh timeout 900 /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws143/comb143.py > scripts/ws143/comb143.log 2>&1
echo "EXIT $? $(date +%T)"

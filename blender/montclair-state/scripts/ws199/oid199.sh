cd /workspace/nj-scenes/montclair-state
DLR=$(( $(date +%s) + ${WAIT:-240} ))
until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-4500} ]; do [ $(date +%s) -ge $DLR ] && { echo TIMEOUT; exit 3; }; sleep 2; done
echo "$(date +%T) GO $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
FILE=$PWD/${F:-montclair_state.blend} CHAIN="$CHAIN" CAM="$CAM" CULL="${CULL:--262,-212,-95,-60}" OUTF=$PWD/renders/test/$(date +%Y%m%d-%H%M)_$N.png WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws198/oid198.py 2>&1 | grep -E "WROTE|rror|WATCH"

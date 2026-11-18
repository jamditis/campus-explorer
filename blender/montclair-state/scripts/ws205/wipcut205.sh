cd /workspace/nj-scenes/montclair-state
DLR=$(( $(date +%s) + ${WAIT:-600} ))
run(){ until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-6000} ]; do [ $(date +%s) -ge $DLR ] && { echo TIMEOUT; return; }; sleep 2; done; T=$(date +%Y%m%d-%H%M); echo "$(date +%T) $3 $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 FILE=$PWD/$4 CHAIN="${6:-}" CAM="$2" CULL="$1" OUTF=$PWD/renders/$5/${T}_$3.jpg SAMP=12 PCT=${PCT:-55} WD_MIN=${WDM:-1500} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws195/runcut195.py 2>&1 | grep -E "WROTE|F205|Trace|rror|WATCH|MEM189"; }
source "$JOBF"
echo WIPDONE

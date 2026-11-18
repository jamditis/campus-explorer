cd /workspace/nj-scenes/montclair-state
DLR=$(date -d "22:45" +%s)
run(){ until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5000 ]; do [ $(date +%s) -ge $DLR ] && { echo TIMEOUT; return; }; sleep 2; done; T=$(date +%Y%m%d-%H%M); echo "$(date +%T) $3 $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 FILE=$PWD/$4 CHAIN="" CAM="$2" CULL="$1" OUTF=$PWD/renders/$5/${T}_$3.jpg SAMP=12 PCT=${PCT:-55} WD_MIN=1000 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws195/runcut195.py 2>&1 | grep -E "WROTE|rror|WATCH"; }
C="-262,-212,-95,-60"; CB="-243.95,-74.59,128.0,-239.38,-80.93,126.0,28"


echo WIPDONE
CE="-233.0,-79.8,128.4,-223.5,-76.0,126.9,26"
run $C "$CE" cut_ws197_E_end_wedge_STILL_PRESENT_ws197c montclair_state_ws197c.blend test
echo WIPDONE

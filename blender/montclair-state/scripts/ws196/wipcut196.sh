cd /workspace/nj-scenes/montclair-state
DLR=$(date -d "22:04" +%s)
run(){ until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge 5000 ]; do [ $(date +%s) -ge $DLR ] && { echo TIMEOUT; return; }; sleep 2; done; T=$(date +%Y%m%d-%H%M); echo "$(date +%T) $3 $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 FILE=$PWD/montclair_state.blend CHAIN="" CAM="$2" CULL="$1" OUTF=$PWD/renders/wip/${T}_$3.jpg SAMP=12 PCT=${PCT:-55} WD_MIN=1000 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws195/runcut195.py 2>&1 | grep -E "WROTE|rror|WATCH"; }
C="-262,-212,-95,-60"
run $C "-243.5,-77.0,128.0,-236.5,-73.5,126.1,28" closeup_ISA_stalls_flush_AFTER_ws196a_cut
run $C "-222.0,-80.5,128.1,-250.0,-86.0,125.6,26" eye_access_lot_from_NE_aisle_AFTER_ws196a_cut
run $C "-257.0,-75.5,128.3,-232.0,-77.5,126.0,26" eye_access_rows_from_W_AFTER_ws196a_cut
echo WIPDONE

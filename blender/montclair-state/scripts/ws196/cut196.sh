cd /workspace/nj-scenes/montclair-state
T=$(date +%Y%m%d-%H%M)
run(){ while pgrep -x blender >/dev/null; do sleep 2; done; echo "$(date +%T) $3 $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 FILE=$PWD/montclair_state.blend CHAIN="$1" CAM="$2" CULL="-262,-212,-95,-60" OUTF=$PWD/renders/test/${T}_$3.jpg SAMP=16 PCT=60 WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws195/runcut195.py 2>&1 | grep -E "WROTE|F196|rror|WATCH"; }
CU="-243.5,-77.0,128.0,-236.5,-73.5,126.1,28"; NE="-222.0,-80.5,128.1,-250.0,-86.0,125.6,26"
for v in "CU:$CU" "NE:$NE"; do n=${v%%:*}; c=${v#*:}
# run "" "$c" cut_ws196_ISA_${n}_BEFORE_ws195a
 run "ws196/fix196.py" "$c" cut_ws196_ISA_${n}_AFTER_fix196
done; echo CUTDONE

cd /workspace/nj-scenes/montclair-state
T=$(date +%Y%m%d-%H%M)
run(){ while pgrep -x blender >/dev/null; do sleep 2; done
 FILE=$PWD/montclair_state.blend CHAIN="$1" CAM="$2" CULL="-275,-200,-110,-65" OUTF=$PWD/renders/test/${T}_$3.jpg SAMP=16 PCT=60 WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws195/runcut195.py 2>&1 | grep -E "WROTE|MEM189|F195 built|rror|WATCH"; }
OB="-266.0,-106.0,136.0,-236.0,-88.0,125.0,26"; EW="-263.0,-87.5,126.6,-238.0,-88.5,125.0,26"; CU="-260.0,-91.0,126.3,-253.0,-84.5,124.3,30"
for v in "OB:$OB" "EW:$EW" "CU:$CU"; do n=${v%%:*}; c=${v#*:}
 run "" "$c" cut_ws195_W6_${n}_BEFORE_ws194d
 run "ws195/fix195.py" "$c" cut_ws195_W6_${n}_AFTER_fix195
done; echo CUTDONE

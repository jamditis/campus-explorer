cd /workspace/nj-scenes/montclair-state
T=$(date +%Y%m%d-%H%M)
run(){ while pgrep -x blender >/dev/null; do sleep 2; done
 FILE=$1 CAM="$2" CULL="$3" OUTF=$PWD/renders/test/${T}_$4.jpg SAMP=16 PCT=60 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws194/runcut194.py 2>&1 | grep -E "WROTE|MEM189|rror|WATCH"; }
PRE=$PWD/montclair_state_pre_20261116ws194.blend; MAIN=$PWD/montclair_state.blend
EC="-300.0,-241.0,118.9,-326.0,-232.0,117.0,26"; ECULL="-345,-295,-256,-225"
WC="-313.0,-239.0,118.6,-292.0,-236.0,118.3,26"; WCULL="-318,-280,-252,-225"
run $PRE "$EC" "$ECULL" cut_eye_ramp_from_E_BEFORE_ws193a
run $MAIN "$EC" "$ECULL" cut_eye_ramp_from_E_AFTER_ws194c
run $PRE "$WC" "$WCULL" cut_eye_strip_from_W_BEFORE_ws193a
run $MAIN "$WC" "$WCULL" cut_eye_strip_from_W_AFTER_ws194c
echo CUTDONE

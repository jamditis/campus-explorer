#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=oy_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/oy/oy_ccis.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
REVERT=1 $B -b $T --python scripts/oy/oy_build.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/oy/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261101oy.blend --python scripts/oj/oj_sig.py -- data/oy/sig_backup.json 2>&1 | grep SIG
cmp data/oy/sig_reverted.json data/oy/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/oy/sig_reverted.json data/oy/sig_backup.json | head; }
sed -e "s/'OW3_CELS_walk_road_curb_lip_UNVERIFIED'/'OW3_CELS_walk_road_curb_lip_UNVERIFIED','Center for Computing and Information Science roof (LiDAR)'/" -e 's/XCHK/XCHK/' /tmp/ox_x.py > /tmp/oy_x.py 2>/dev/null || true
$B -b $T --python /tmp/oy_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261101oy.blend --python /tmp/oy_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

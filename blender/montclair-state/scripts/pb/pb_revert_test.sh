#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=pb_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/pb/pb_fan.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/pb/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261101pb.blend --python scripts/oj/oj_sig.py -- data/pb/sig_backup.json 2>&1 | grep SIG
$B -b montclair_state.blend --python scripts/oj/oj_sig.py -- data/pb/sig_final.json 2>&1 | grep SIG
cmp data/pb/sig_reverted.json data/pb/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/pb/sig_reverted.json data/pb/sig_backup.json | head; }
$B -b $T --python scripts/oz/oz_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261101pb.blend --python scripts/oz/oz_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

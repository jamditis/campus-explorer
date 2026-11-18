#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=oz_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/oz/oz_joints.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
REVERT=1 $B -b $T --python scripts/oz/oz_ccis.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/oz/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261101oz.blend --python scripts/oj/oj_sig.py -- data/oz/sig_backup.json 2>&1 | grep SIG
cmp data/oz/sig_reverted.json data/oz/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/oz/sig_reverted.json data/oz/sig_backup.json | head; }
$B -b $T --python scripts/oz/oz_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261101oz.blend --python scripts/oz/oz_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

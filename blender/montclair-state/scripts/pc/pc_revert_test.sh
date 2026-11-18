#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=pc_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/pc/pc_fillet_grass.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/pc/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261101pc.blend --python scripts/oj/oj_sig.py -- data/pc/sig_backup.json 2>&1 | grep SIG
$B -b montclair_state.blend --python scripts/oj/oj_sig.py -- data/pc/sig_final.json 2>&1 | grep SIG
cmp data/pc/sig_reverted.json data/pc/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/pc/sig_reverted.json data/pc/sig_backup.json | head; }
$B -b $T --python scripts/oz/oz_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261101pc.blend --python scripts/oz/oz_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

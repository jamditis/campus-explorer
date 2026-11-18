#!/bin/bash
# ok revert test: copy final -> REVERT=1 ok_berm, ok_cam, ok_build (-- --save) -> oj_sig vs backup
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=ok_revert_test.blend
cp montclair_state.blend $T
for s in ok_berm ok_cam ok_build; do REVERT=1 $B -b $T --python scripts/ok/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
$B -b $T --python scripts/oj/oj_sig.py -- data/ok/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031ok.blend --python scripts/oj/oj_sig.py -- data/ok/sig_backup.json 2>&1 | grep SIG
cmp data/ok/sig_reverted.json data/ok/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/ok/sig_reverted.json data/ok/sig_backup.json | head; }
rm -f $T ${T}1

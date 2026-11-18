#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=os_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/os/os_build.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/os/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031os.blend --python scripts/oj/oj_sig.py -- data/os/sig_backup.json 2>&1 | grep SIG
cmp data/os/sig_reverted.json data/os/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/os/sig_reverted.json data/os/sig_backup.json | head; }
cat > /tmp/os_x.py <<'Q'
import bpy
print('XCHK',sorted((o.name,[m.name for m in o.data.materials]) for o in bpy.data.collections['OR_skirt_base_course_20261031or'].objects),bpy.data.materials['OR_skirt_base_course_grey_dirt_UNVERIFIED'].use_fake_user,'OS_skirt_base_course_dark_dirt_UNVERIFIED' in bpy.data.materials, bpy.data.collections.get('OS_skirt_sill_drips_20261031os'))
Q
$B -b $T --python /tmp/os_x.py 2>&1 | grep XCHK | md5sum; $B -b montclair_state_pre_20261031os.blend --python /tmp/os_x.py 2>&1 | grep XCHK | md5sum
rm -f $T ${T}1

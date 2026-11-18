#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=on_revert_test.blend
cp montclair_state.blend $T
for s in on_blind on_cam on_infill on_fix_shard; do REVERT=1 $B -b $T --python scripts/on/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
$B -b $T --python scripts/oj/oj_sig.py -- data/on/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031on.blend --python scripts/oj/oj_sig.py -- data/on/sig_backup.json 2>&1 | grep SIG
cmp data/on/sig_reverted.json data/on/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/on/sig_reverted.json data/on/sig_backup.json | head; }
rm -f $T ${T}1
cat > /tmp/on_x.py <<'Q'
import bpy, hashlib
me=bpy.data.objects['Schmitt Hall walls'].data
h=hashlib.sha1(b''.join(v.co.to_tuple(5).__repr__().encode() for v in me.vertices)).hexdigest()[:12]
o=bpy.data.objects['CCOM_Win_Wing_A_blind'];s=o.material_slots[0]
print('XCHK',s.link,s.material.name,len(me.polygons),len(me.vertices),h,len(bpy.data.objects),len(bpy.data.meshes),len(bpy.data.collections))
Q
cp montclair_state.blend $T; for s in on_blind on_cam on_infill on_fix_shard; do REVERT=1 $B -b $T --python scripts/on/$s.py -- --save 2>&1 | grep -E "Error|Trace"; done
$B -b $T --python /tmp/on_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261031on.blend --python /tmp/on_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

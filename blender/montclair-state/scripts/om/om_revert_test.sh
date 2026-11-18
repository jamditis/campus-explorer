#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=om_revert_test.blend
cp montclair_state.blend $T
for s in om_cam om_build; do REVERT=1 $B -b $T --python scripts/om/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
$B -b $T --python scripts/oj/oj_sig.py -- data/om/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031om.blend --python scripts/oj/oj_sig.py -- data/om/sig_backup.json 2>&1 | grep SIG
cmp data/om/sig_reverted.json data/om/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/om/sig_reverted.json data/om/sig_backup.json | head; }
cat > /tmp/om_x.py <<'Q'
import bpy; c=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps'].data
print('XCHK',[m.name for m in c.materials],sorted(set(p.material_index for p in c.polygons)),bpy.data.objects['CCOM_Win_Wing_A_blind'].data.materials[0].name,
 [round(bpy.data.objects[n].location.z,4) for n in ('T_RedMaple_L1_0511','Lamp_acorn_049')],len(bpy.data.objects),len(bpy.data.materials))
Q
$B -b $T --python /tmp/om_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261031om.blend --python /tmp/om_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

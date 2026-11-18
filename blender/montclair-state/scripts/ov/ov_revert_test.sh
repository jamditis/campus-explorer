#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=ov_revert_test.blend
cp montclair_state.blend $T
for s in ov_build3 ov_build2 ov_build; do REVERT=1 $B -b $T --python scripts/ov/$s.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"; done
$B -b $T --python scripts/oj/oj_sig.py -- data/ov/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031ov.blend --python scripts/oj/oj_sig.py -- data/ov/sig_backup.json 2>&1 | grep SIG
cmp data/ov/sig_reverted.json data/ov/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/ov/sig_reverted.json data/ov/sig_backup.json | head; }
cat > /tmp/ov_x.py <<'P'
import bpy, hashlib
h=hashlib.sha1()
o=bpy.data.objects['Footpaths_OSM']; h.update(str([m.name for m in o.modifiers]).encode()); h.update(str(sorted(o.keys())).encode())
h.update(str([(s.link,s.material.name if s.material else None) for s in o.material_slots]).encode())
for v in o.data.vertices: h.update(('%.4f %.4f %.4f'%tuple(v.co)).encode())
h.update(str(sorted((m.name,m.use_fake_user,sorted(m.keys())) for m in bpy.data.materials)).encode())
h.update(str(sorted(g.name for g in bpy.data.node_groups)).encode())
h.update(str(sorted(c.name for c in bpy.data.collections)).encode())
h.update(str(sorted(o.name for o in bpy.data.objects)).encode()); h.update(str(sorted(m.name for m in bpy.data.meshes)).encode())
for n in [x.name for x in bpy.data.objects if x.name.startswith('OO_skirt_')]:
    me=bpy.data.objects[n].data; h.update(n.encode())
    for v in me.vertices: h.update(('%.4f %.4f %.4f'%tuple(v.co)).encode())
print('XCHK',h.hexdigest())
P
$B -b $T --python /tmp/ov_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261031ov.blend --python /tmp/ov_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

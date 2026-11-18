#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=ou_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/ou/ou_build.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/ou/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031ou.blend --python scripts/oj/oj_sig.py -- data/ou/sig_backup.json 2>&1 | grep SIG
cmp data/ou/sig_reverted.json data/ou/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/ou/sig_reverted.json data/ou/sig_backup.json | head; }
cat > /tmp/ou_x.py <<'P'
import bpy, hashlib
h=hashlib.sha1()
for o in sorted(bpy.data.collections['OR_skirt_base_course_20261031or'].objects,key=lambda o:o.name):
    h.update((o.name+str([m.name for m in o.data.materials])+str(sorted(a.name for a in o.data.attributes))).encode())
    for v in o.data.vertices: h.update(('%.4f %.4f %.4f'%tuple(v.co)).encode())
for n in ('Context_skirt_3DEP_ortho_4km','Footpaths_OSM','Roads_OSM'): o=bpy.data.objects[n]; h.update((n+str([m.name for m in o.modifiers])+str(sorted(o.keys()))).encode())
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.name.startswith('T_'): h.update(('%s%.4f%s'%(o.name,o.location.z,sorted(o.keys()))).encode())
h.update(str([(m.name,m.use_fake_user) for m in bpy.data.materials if 'base_course' in m.name]).encode())
h.update(str(sorted(g.name for g in bpy.data.node_groups)).encode())
h.update(str([(m.name,m.use_fake_user) for m in bpy.data.materials if 'skirt' in m.name.lower()]).encode()); h.update(str([s.material.name for s in bpy.data.objects['Context_skirt_3DEP_ortho_4km'].material_slots]).encode()); h.update(str(sorted(c.name for c in bpy.data.collections)).encode())
print('XCHK',h.hexdigest())
P
$B -b $T --python /tmp/ou_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261031ou.blend --python /tmp/ou_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=ot_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/ot/ot_cam.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Error|Trace"
REVERT=1 $B -b $T --python scripts/ot/ot_build.py -- --save 2>&1 | grep -E "restored|REVERTED|SAVED|Error|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/ot/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261031ot.blend --python scripts/oj/oj_sig.py -- data/ot/sig_backup.json 2>&1 | grep SIG
cmp data/ot/sig_reverted.json data/ot/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/ot/sig_reverted.json data/ot/sig_backup.json | head; }
cat > /tmp/ot_x.py <<'P'
import bpy, hashlib
h=hashlib.sha1()
for o in sorted(bpy.data.collections['OR_skirt_base_course_20261031or'].objects,key=lambda o:o.name):
    h.update((o.name+str([m.name for m in o.data.materials])+str(sorted(a.name for a in o.data.attributes))).encode())
    for v in o.data.vertices: h.update(('%.4f'%v.co.z).encode())
for n in ('Context_skirt_3DEP_ortho_4km','Footpaths_OSM','Roads_OSM'): o=bpy.data.objects[n]; h.update((n+str([m.name for m in o.modifiers])+str(sorted(o.keys()))).encode())
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.name.startswith('T_'): h.update(('%s%.4f%s'%(o.name,o.location.z,sorted(o.keys()))).encode())
h.update(str([(m.name,m.use_fake_user) for m in bpy.data.materials if 'base_course' in m.name]).encode())
h.update(str(sorted(g.name for g in bpy.data.node_groups)).encode())
print('XCHK',h.hexdigest())
P
$B -b $T --python /tmp/ot_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261031ot.blend --python /tmp/ot_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

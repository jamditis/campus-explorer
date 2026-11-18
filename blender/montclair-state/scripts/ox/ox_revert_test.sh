#!/bin/bash
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; T=ox_revert_test.blend
cp montclair_state.blend $T
REVERT=1 $B -b $T --python scripts/ox/ox_build.py -- --save 2>&1 | grep -E "REVERTED|SAVED|Trace"
$B -b $T --python scripts/oj/oj_sig.py -- data/ox/sig_reverted.json 2>&1 | grep SIG
$B -b montclair_state_pre_20261101ox.blend --python scripts/oj/oj_sig.py -- data/ox/sig_backup.json 2>&1 | grep SIG
cmp data/ox/sig_reverted.json data/ox/sig_backup.json && echo REVERT MATCH || { echo REVERT DIFF; diff data/ox/sig_reverted.json data/ox/sig_backup.json | head; }
cat > /tmp/ox_x.py <<'P'
import bpy, hashlib
h=hashlib.sha1()
for n in ('Footpaths_OSM','Context_skirt_3DEP_ortho_4km','Roads_OSM','Terrain_LiDAR_DTM_1m','OW3_CELS_walk_road_curb_lip_UNVERIFIED'):
    o=bpy.data.objects[n]; h.update(str((o.hide_render,o.hide_viewport)).encode()); h.update(str([(m.name,m.show_viewport,m.show_render) for m in o.modifiers]).encode()); h.update(str(sorted(o.keys())).encode())
    h.update(str([(s.link,s.material.name if s.material else None) for s in o.material_slots]).encode())
    if n=='Footpaths_OSM':
        for v in o.data.vertices: h.update(('%.4f %.4f %.4f'%tuple(v.co)).encode())
h.update(str(sorted((m.name,m.use_fake_user,sorted(m.keys())) for m in bpy.data.materials)).encode())
h.update(str(sorted(g.name for g in bpy.data.node_groups)).encode())
h.update(str(sorted(c.name for c in bpy.data.collections)).encode())
h.update(str(sorted(o.name for o in bpy.data.objects)).encode()); h.update(str(sorted(m.name for m in bpy.data.meshes)).encode()); h.update(str(sorted(m.name for m in bpy.data.cameras)).encode())
print('XCHK',h.hexdigest())
P
$B -b $T --python /tmp/ox_x.py 2>&1 | grep XCHK; $B -b montclair_state_pre_20261101ox.blend --python /tmp/ox_x.py 2>&1 | grep XCHK
rm -f $T ${T}1

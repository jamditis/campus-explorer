"""2026-10-21 session dU2 (~9:50 AM ET). The LiDAR DTM terrain (Terrain_LiDAR_DTM_1m, grass material) ran THROUGH CCOM's 1st-floor
interior: 0.4-1.1 m above the dd terrazzo corridor floors (seen as a grass hump inside the south corridor at eye level).
Joe's photos 04/05 show a flat terrazzo floor / charcoal rugs the whole way -> push only the terrain vertices that lie under a CCOM
interior floor (dd_*floor* in CCOM_1f_interior_full_dd + dc floor objects) down to 0.12 m below that floor. Original z kept in
attribute dU2_orig_z (+ prop) -> REVERT=1 restores. Idempotent. Nothing outside the floor footprints moves. SAVE=1 saves."""
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T = bpy.data.objects['Terrain_LiDAR_DTM_1m']; me = T.data; assert T.library is None and me.library is None
mw = T.matrix_world; mi = mw.inverted()
A = me.attributes.get('dU2_orig_z')
if A is not None:  # restore first (idempotent)
    # world z restore
    for v, a in zip(me.vertices, A.data):
        if a.value > -1e8:
            w = mw @ v.co; w.z = a.value; v.co = mi @ w
    me.attributes.remove(A)
if os.environ.get('REVERT') == '1':
    me.update(); print('DU2TER reverted', flush=True)
else:
    fl = [o for o in bpy.data.collections['CCOM_1f_interior_full_dd'].all_objects if o.type == 'MESH' and 'floor' in o.name]
    fl += [o for o in bpy.data.collections['CCOM_east_interior_joe_20261020dc'].all_objects if o.type == 'MESH' and 'floor' in o.name.lower()]
    bm = bmesh.new()
    for o in fl:
        t = bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world); m2 = bpy.data.meshes.new('_t'); t.to_mesh(m2); t.free(); bm.from_mesh(m2); bpy.data.meshes.remove(m2)
    tree = BVHTree.FromBMesh(bm); bm.free()
    A = me.attributes.new('dU2_orig_z', 'FLOAT', 'POINT'); n = 0; mx = 0
    for v, a in zip(me.vertices, A.data):
        a.value = -1e9; w = mw @ v.co
        if not (-25 < w.x < 30 and -26 < w.y < 6): continue
        h = tree.ray_cast(Vector((w.x, w.y, 150.0)), Vector((0, 0, -1)), 30.0)
        if h[0] is None: continue
        zf = h[0].z
        if w.z > zf - 0.12:
            a.value = w.z; mx = max(mx, w.z - (zf - 0.12)); w.z = zf - 0.12; v.co = mi @ w; n += 1
    me.update(); T['dU2_note'] = 'dU2: %d terrain verts under CCOM interior floors lowered (orig z in attr dU2_orig_z)' % n
    print('DU2TER floors', len(fl), [o.name for o in fl], 'verts', n, 'max_drop', round(mx, 3), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DU2TER_SAVED', flush=True)

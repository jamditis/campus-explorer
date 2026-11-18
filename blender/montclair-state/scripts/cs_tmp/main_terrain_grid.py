import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T = bpy.data.objects['Terrain_LiDAR_DTM_1m']
b = bmesh.new(); b.from_mesh(T.data); b.transform(T.matrix_world); tb = BVHTree.FromBMesh(b); b.free()
xs = np.arange(-215, -60, 0.5); ys = np.arange(-110, -30, 0.5); Z = np.full((len(ys), len(xs)), np.nan)
for j, y in enumerate(ys):
    for i, x in enumerate(xs):
        h = tb.ray_cast(Vector((x, y, 300)), Vector((0, 0, -1)))
        if h[0] is not None: Z[j, i] = h[0].z
np.savez('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cs/main_terrain_cole_plaza_cs.npz', xs=xs, ys=ys, z=Z)
print('cs main grid', Z.shape, np.nanmin(Z), np.nanmax(Z))
K = bpy.data.objects['Alexander Kasser Theater walls']; b = bmesh.new(); b.from_mesh(K.data); b.transform(K.matrix_world); kb = BVHTree.FromBMesh(b); b.free()
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name.startswith(('Susan A. Cole Hall', 'Cole Hall ', 'COLE_', 'Plaza long')):
        b = bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); ob = BVHTree.FromBMesh(b)
        ov = ob.overlap(kb)
        if ov:
            fs = b.faces; b.faces.ensure_lookup_table()
            cs = [tuple(round(c, 1) for c in b.faces[p[0]].calc_center_median()) for p in ov[:4]]
            print('cs main Kasser-walls overlap', o.name[:40], len(ov), cs)
        b.free()

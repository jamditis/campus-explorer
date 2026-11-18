"""wb: QT_soil_edge_313027435 outer-edge verts on the RZ2 (west/north) side sat 1-3 cm above RZ2 and read as a tan band in the W eye. Lower-only: set them to RZ2 top -0.5 cm so the lawn edge meets the slab lip."""
import bpy,numpy as np,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
RZ=bvh(O['RZ2_SC_LiDAR_ground_patch_UNVERIFIED'])
t=O['QT_soil_edge_313027435_UNVERIFIED']; S=bvh(O['QS_footway_313027435_UNVERIFIED']); mw=t.matrix_world; inv=mw.inverted()
np.save(f'{R}/data/wb/QT435_pre_tuck.npy',np.array([v.co[:] for v in t.data.vertices]))
done=set(); L=[]
for p in t.data.polygons:
    vi=list(p.vertices); ws=[mw@t.data.vertices[i].co for i in vi]; d=[S.find_nearest(v)[3] for v in ws]
    for j in np.argsort(d)[2:]:
        if vi[j] in done: continue
        v=ws[j]; h=RZ.ray_cast(Vector((v.x,v.y,v.z+0.5)),Vector((0,0,-1)))
        if h[0] is None: continue
        z=h[0].z-0.005
        if v.z>z and v.z-z<0.08: t.data.vertices[vi[j]].co=inv@Vector((v.x,v.y,z)); done.add(vi[j]); L.append(round(v.z-z,3))
t.data.update(); print('TUCK',len(L),np.median(L) if L else 0,max(L) if L else 0)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O))

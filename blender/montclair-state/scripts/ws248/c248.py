# ws248: clearance above the stand pad just W of the back walk (what sits over a fill wedge there?)
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W='WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level'
N=['fse_stand_risers','fse_stand_seating','fse_stand_understructure','fse_stand_rails','fse_stand_entry_steps','fse_press_box','WS243_edge_wall_fse_stand_under_pad_UNVERIFIED','fse_stand_under_pad',W]
with bpy.data.libraries.load(F) as (a,b): b.objects=N
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    t=BVHTree.FromPolygons(vs,[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return t
B={o.name:bvh(o) for o in b.objects if o.name!=W}
me=bpy.data.objects[W].data; V=np.array([v.co[:] for v in me.vertices]).reshape(-1,6,3)
for i in range(0,len(V),6):
    r=V[i]; w0=r[0]; d=w0[:2]-r[3][:2]; d/=np.linalg.norm(d); out=[]
    for off in (0.1,0.6,1.2,2.0):
        p=w0[:2]+d*off; hits=[]
        for n,t in B.items():
            h=t.ray_cast(Vector((p[0],p[1],120)),Vector((0,0,1)),40)
            # first surface from below; also lowest of the structure
            if h[0] is not None: hits.append((round(h[0].z,2),n[4:14]))
        hits.sort(); out.append(hits[:3])
    print('C248 y %.1f walk %.2f'%(w0[1],w0[2]),out,flush=True)
sys.stdout.flush(); os._exit(0)

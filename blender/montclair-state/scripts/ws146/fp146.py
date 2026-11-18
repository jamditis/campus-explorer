
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh_of(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
asp=[o for o in bpy.data.objects if o.name.startswith(('WS142_Lot9_asphalt','WS145')) and o.type=='MESH' and 'curb' not in o.name.lower()]
print("ASP",[o.name[:50] for o in asp])
fc=[o for o in bpy.data.objects if o.name.startswith('WS143_Freeman_NE_forecourt_concrete')]
T=[(o.name,bvh_of(o)) for o in asp]
F=[(o.name,bvh_of(o)) for o in fc]
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world; inv=mw.inverted()
n=0; nf=0
for v in fp.data.vertices:
    w=mw@v.co
    if not (-82<w.x<-60 and -210<w.y<-164): continue
    best=None
    for nm,t in T+F:
        h=t.ray_cast(Vector((w.x,w.y,w.z+1.0)),Vector((0,0,-1)),2.0)
        if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
    if best is not None and w.z > best-0.05:
        w.z=best-0.06; v.co=inv@w; n+=1
fp.data.update()
print("PUSHED_FP",n)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws146a.blend',copy=True)
print("SAVED")

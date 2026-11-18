# UNIFY #52 decision + candidate fix (ws147; NOT run on main — memory-blocked).
# Evidence: 2023 LiDAR intensity has NO bright curb band (8-11k) at the walk-nose W end: walk concrete 5.8-6k at x -72..-71, y <= -206.5
# meets asphalt 2.4-3k directly at y ~ -206.2; the bright curb band starts at (-70.5,-207.0) and runs SSE. Raw class-2 z profiles across
# y -205..-208 are smooth (<=6 cm per 0.5 m, ground falls S, the asphalt is UPHILL of the walk). => the W end is a deliberate FLUSH
# joint (accessible lot-to-walk route), not a raised curb. Built taper (8.7 cm -> 0) is right in kind; fix = make it a clean
# 1.2 m linear curb-end drop and set the walk edge 5 mm ABOVE the asphalt over the flush stretch (walk was 1 cm below).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    b=bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); return t
curb=[o for o in bpy.data.objects if o.name.startswith('WS145_walk_N_nose_curb')][0]
asp=[o for o in bpy.data.objects if o.name.startswith('WS145_walk_nose_lot_asphalt')][0]
walk=[o for o in bpy.data.objects if o.name.startswith('WS136a_Skyline_W_walk_N_of_-248')][0]
TA=bvh(asp)
def az(x,y):
    h=TA.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
# 1) curb: top verts within 1.2 m of the W end (x < -71.1) -> linear reveal 0.10 -> 0.00 toward x -72.3
mw=curb.matrix_world; inv=mw.inverted(); n=0
for v in curb.data.vertices:
    w=mw@v.co
    if w.x< -71.1 and -207.3<w.y< -205.8:
        a=az(w.x,w.y+0.3) or az(w.x,w.y+0.6)
        if a is None: continue
        t=max(0.0,min(1.0,(w.x+72.3)/1.2)); top=a+0.10*t+0.005
        if w.z>a-0.02: w.z=min(w.z,top) if w.z>top else max(w.z,a+0.005); v.co=inv@w; n+=1
curb.data.update(); print("FIX52_CURB_VERTS",n)
# 2) walk edge verts on the flush stretch: >= asphalt + 5 mm
mw=walk.matrix_world; inv=mw.inverted(); m=0
for v in walk.data.vertices:
    w=mw@v.co
    if -72.4<w.x<-71.0 and -207.0<w.y<-205.9:
        a=az(w.x,w.y+0.25)
        if a is not None and w.z<a+0.005: w.z=a+0.005; v.co=inv@w; m+=1
walk.data.update(); print("FIX52_WALK_VERTS",m)

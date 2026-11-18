# ws174b: after the move, sink any lawn/ground vertex that now sits above the new curb/walk/drive (old road band) or above the stretched lip
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def bv(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); m.transform(o.matrix_world)
    b=BVHTree.FromPolygons([v.co.copy() for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); oe.to_mesh_clear(); return b
COV=[bv(o) for o in OB if o.type=='MESH' and o.name.startswith(('WS163_NormalAve_W_S_curb','WS163_NormalAve_W_S_sidewalk','WS163_walk_back_lawn_lip_S','WS173_driveway'))]
def cz(x,y):
    z=None
    for b in COV:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None and (z is None or h[0].z>z): z=h[0].z
    return z
for n in ['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED','WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5']:
    o=OB.get(n)
    if not o: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
        if not (-79.5<t<-0.5 and -14.6<s<-9.8): continue
        z=cz(w.x,w.y)
        lim=(0.03 if s<-12.0 else 0.06)
        if z is not None and w.z>z-lim: w.z=z-lim-0.02; v.co=mi@w; k+=1
    o.data.update(); print('FIX174b sunk',n,k,flush=True)

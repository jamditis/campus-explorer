# ws179 READ-ONLY probe (run inside Blender on main or the sub178-style subset): what currently occupies the College Ave S-leg mouth
# (OSM 232846669, LiDAR asphalt t 4.8..15.8 / leg t 5.25..13.25) on the S side of Normal Ave WS110. Prints per object: verts/faces in the
# window t 1..21, s -27..-9 (ws173 road frame), z range, and evaluated top z on a probe grid. Writes nothing.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def st(x,y): d=np.array((x,y))-A; return float(d@N), float(d@T)
def xy(s,t): p=A+N*s+T*t; return float(p[0]),float(p[1])
dg=bpy.context.evaluated_depsgraph_get(); hits={}
for o in OB:
    if o.type!='MESH' or o.hide_render: continue
    if 'CAM' in o.name or 'skirt' in o.name.lower(): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(c.x for c in bb)<-270 or min(c.x for c in bb)>-245 or max(c.y for c in bb)<-295 or min(c.y for c in bb)>-268: continue
    oe=o.evaluated_get(dg); m=oe.to_mesh(); mw=o.matrix_world; n=0; zs=[]
    for v in m.vertices:
        w=mw@v.co; s,t=st(w.x,w.y)
        if 1<=t<=21 and -27<=s<=-9: n+=1; zs.append(w.z)
    if n:
        hits[o.name]=BVHTree.FromPolygons([mw@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons])
        print('PROBE179 obj %-70s verts_in %5d z %.2f..%.2f'%(o.name[:70],n,min(zs),max(zs)),flush=True)
    oe.to_mesh_clear()
print('PROBE179 grid: s rows, t cols 2..20 step 2 -> topmost object initials + z',flush=True)
for s in (-10.0,-10.6,-11.3,-12.0,-12.8,-14,-17,-20,-23,-26):
    row=[]
    for t in range(2,21,2):
        x,y=xy(s,t); best=None
        for nm,b in hits.items():
            h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
            if h[0] is not None and (best is None or h[0].z>best[1]): best=(nm,h[0].z)
        row.append('%s:%.2f'%(best[0][:12],best[1]) if best else '-')
    print('PROBE179 s %6.1f  %s'%(s,' | '.join(row)),flush=True)

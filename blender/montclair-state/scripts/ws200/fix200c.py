# ws200 W19 (new): the wavy WS75/WS80 seam (pre-existing dark line with nicks, visible once W18 removed the bumps; close-up 0144 BEFORE / 0143 AFTER).
# RAISE-ONLY: in the W18 bay (x -263..-216, y -107..-95.5) every WS75/WS80 vertex within 0.6 m (plan) of the OTHER sheet is lifted to 3 mm under
# the top of the two sheets at that point (never lowered) -> both edges meet at one level; no coplanar faces (3 mm).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
S2=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS80_sprague_lot_fill_asphalt'))]
def bv(o):
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]; return BVHTree.FromPolygons(V,[tuple(p.vertices) for p in o.data.polygons]),V
B={o.name:bv(o) for o in S2}
def inb(x,y): return -263<x<-216 and -107<y<-95.5
tot=0;mx=0
for o in S2:
    other=[p for p in S2 if p is not o][0]; To,Vo=B[other.name]; Ts,_=B[o.name]
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        p=mw@v.co
        if not inb(p.x,p.y): continue
        loc=To.find_nearest(p,0.6)[0]
        if loc is None or (Vector((loc.x-p.x,loc.y-p.y)).length>0.6): continue
        zs=[]
        for T in (To,Ts):
            h=T.ray_cast(Vector((p.x,p.y,p.z+2)),Vector((0,0,-1)),4)
            if h[0]: zs.append(h[0].z)
        h=To.ray_cast(Vector((p.x,p.y,p.z+2)),Vector((0,0,-1)),4)
        zt=(h[0].z if h[0] else loc.z)
        tgt=max(p.z,zt-0.003) if zt>p.z else p.z
        if tgt>p.z+1e-4: mx=max(mx,tgt-p.z); p.z=tgt; v.co=mi@p; tot+=1
    o.data.update()
print('F200c seam lifted',tot,'verts max',round(mx,3),flush=True)

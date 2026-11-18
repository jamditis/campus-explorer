"""wi2 pass 2 (clumped, target 12/m2 to match near lawn 10.5/m2 + its clumping): densify grass tufts on the Stone verge strip (between Stone footway 546643369 and service road 546643370)
from ~4.9 to ~7.5 pts/m2 (lawn beyond ~7.0). Adds points to QS_Richardson_lawn_grass_points_UNVERIFIED, seated on
the top ground surface, kept >=0.15 m from any slab edge. Vertex adds only."""
import bpy, json, random, numpy as np, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(20261110)
O=bpy.data.objects; R='/workspace/nj-scenes/montclair-state'
C=json.load(open(R+'/scripts/wi2/cells.json')); step=0.5; TGT=float(__import__("os").environ.get("TGT","12"))
def bv(o,flat=False):
    m=o.matrix_world; V=[m@v.co for v in o.data.vertices]
    if flat: V=[Vector((v.x,v.y,0)) for v in V]
    return BVHTree.FromPolygons(V,[tuple(p.vertices) for p in o.data.polygons])
slabn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QS_service_','QW_footway_','QT_soil_edge_')) ]
SF=[bv(O[n],True) for n in slabn]
GR=[bv(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone_west_LiDAR','QW_DTM'))]
def gz(x,y):
    z=[]
    for b in GR:
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None: z.append(h[0].z)
    return max(z) if z else None
def clear(x,y):
    p=Vector((x,y,0))
    for b in SF:
        f=b.find_nearest(p,0.15)
        if f[0] is not None: return False
    return True
g=O['QS_Richardson_lawn_grass_points_UNVERIFIED']; m=g.matrix_world; mi=m.inverted()
cnt={}
for gn in ['QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED']:
    gg=O[gn]; mm=gg.matrix_world
    for v in gg.data.vertices:
        c=mm@v.co; k=(round(130+np.floor((c.x-130)/step)*step,2),round(280+np.floor((c.y-280)/step)*step,2)); cnt[k]=cnt.get(k,0)+1
bm=bmesh.new(); bm.from_mesh(g.data); add=0
for k in C['verge']:
    k=tuple(k); have=cnt.get(k,0); want=TGT*step*step
    n=int(want-have+random.random())
    cx=cy=0
    for i in range(max(0,n)):
        for t in range(6):
            cx=k[0]+0.1+random.random()*0.3 if i==0 or t>2 else cx; cy=k[1]+0.1+random.random()*0.3 if i==0 or t>2 else cy; x=cx+random.gauss(0,0.09); y=cy+random.gauss(0,0.09)
            if not clear(x,y): continue
            z=gz(x,y)
            if z is None: continue
            bm.verts.new(mi@Vector((x,y,z))); add+=1; break
bm.to_mesh(g.data); bm.free(); g.data.update()
print('ADDED',add,'verge m2',len(C['verge'])*step*step)
bpy.ops.wm.save_mainfile()
print('SAVED')

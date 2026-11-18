"""wk: thin tuft band along the service road's WEST edge (0.15-1.0 m off the road, y264-290): 7.5 and 27/m2 vs ~39/m2 beyond.
Adds clumped points to QS_Richardson_lawn_grass_points_UNVERIFIED on the top ground sheet, >=0.15 m from any slab/soil strip."""
import bpy,random,numpy as np,bmesh,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
random.seed(20261109); O=bpy.data.objects
def bv(o,flat=False):
    m=o.matrix_world; V=[m@v.co for v in o.data.vertices]
    if flat: V=[Vector((v.x,v.y,0)) for v in V]
    return BVHTree.FromPolygons(V,[tuple(p.vertices) for p in o.data.polygons])
slabn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QS_service_','QW_footway_','QT_soil_edge_','TR_footway','SG_'))]
SF=[bv(O[n],True) for n in slabn]; RD=bv(O['QS_service_546643370_UNVERIFIED'],True)
GR=[bv(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone_west_LiDAR','QW_DTM','WT_richardson_west_LiDAR','WU_richardson_reid','RZ2_','WF_east_dorm_LiDAR','Terrain_LiDAR'))]
def gz(x,y):
    z=[h[0].z for b in GR for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
def clear(x,y):
    p=Vector((x,y,0)); return all(b.find_nearest(p,0.15)[0] is None for b in SF)
def band(x,y):
    p=Vector((x,y,0))
    if any(b.ray_cast(p+Vector((0,0,1)),Vector((0,0,-1)),2)[0] is not None for b in SF): return None
    h=RD.find_nearest(p,1.2)
    if h[0] is None or h[0].x<=x: return None  # road must be east of the point
    return h[3]
g=O['QS_Richardson_lawn_grass_points_UNVERIFIED']; mi=g.matrix_world.inverted()
bm=bmesh.new(); bm.from_mesh(g.data); add=0; tries=0
# clumps: centres in the band, 3-6 tufts each
while add<int(sys.argv[-1] if sys.argv[-1].isdigit() else 170) and tries<20000:
    tries+=1; x=random.uniform(112,132); y=random.uniform(264,290); d=band(x,y)
    if d is None or not (0.15<=d<=1.0): continue
    for i in range(random.randint(3,6)):
        px=x+random.gauss(0,0.1); py=y+random.gauss(0,0.1); dd=band(px,py)
        if dd is None or not (0.15<=dd<=1.05) or not clear(px,py): continue
        z=gz(px,py)
        if z is None: continue
        bm.verts.new(mi@Vector((px,py,z))); add+=1
bm.to_mesh(g.data); bm.free(); g.data.update(); print('ADDED',add,'tries',tries,flush=True)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)

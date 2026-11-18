import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
G=['WV_stone_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
S=['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','QS_service_546643370_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','QW_soil_edge_546643369_ext_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED','SG_QuadRoad_full_313028548_549_UNVERIFIED','TR_footway_546643369_S_gap_UNVERIFIED']
H=['TI_Stone_Hall_313028565_lower_UNVERIFIED','TQ_Stone_fascia_lower_UNVERIFIED']
def bv(n):
    o=O[n]; m=o.data; return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons])
GB={n:bv(n) for n in G}; SB={n:bv(n) for n in S}; HB={n:bv(n) for n in H}
def top(B,x,y):
    z=None;nm=None
    for n,b in B.items():
        r=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if r[0] is not None and (z is None or r[0].z>z): z=r[0].z;nm=n
    return z,nm
# building base: lowest z of lower mesh
lo=O['TI_Stone_Hall_313028565_lower_UNVERIFIED']; print('HALL zmin',min((lo.matrix_world@v.co).z for v in lo.data.vertices))
out=[]
for x in np.arange(126,150,0.1):
  for y in np.arange(250,322,0.1):
    hz,_=top(HB,x,y)
    if hz is not None: continue
    g,gn=top(GB,x,y)
    if g is None: continue
    s,sn=top(SB,x,y)
    # distance to building: check 8 dirs within 1.5m
    near=None
    for d in (0.2,0.4,0.7,1.0,1.5):
        for a in range(0,360,45):
            import math
            if top(HB,x+d*math.cos(math.radians(a)),y+d*math.sin(math.radians(a)))[0] is not None: near=d;break
        if near: break
    if near is None: continue
    out.append([round(x,1),round(y,1),gn[:4],round(g,3),(sn or '')[:6],round(s,3) if s else None,near])
json.dump(out,open('data/wx/probe3.json','w'))
print('N',len(out),flush=True)

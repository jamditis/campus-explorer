import bpy,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
def bvh(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
F=bvh(O['QS_footway_546643369_UNVERIFIED']); R=bvh(O['QS_service_546643370_UNVERIFIED']); FX=bvh(O['QW_footway_546643369_ext_UNVERIFIED'])
G={n:bvh(O[n]) for n in ['QW_DTM_north_edge_ramp_UNVERIFIED','Terrain_LiDAR_DTM_1m','WV_stone_west_LiDAR_patch_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED']}
def z(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return None if h[0] is None else round(h[0].z,3)
for y in [258,262,266,270,274,278,282,286]:
    row=[]
    for x in np.arange(118,150,0.5):
        f=z(F,x,y) or z(FX,x,y); r=z(R,x,y); g=max([v for v in [z(b,x,y) for b in G.values()] if v is not None] or [None]) if any(z(b,x,y) is not None for b in G.values()) else None
        row.append(('F' if f else 'R' if r else '.'))
    print(y,''.join(row))
# transects: for each y, find footway west edge x and road east edge x, ground profile between
for y in np.arange(256,290,2.0):
    xs=np.arange(115,152,0.1); fx=[x for x in xs if (z(F,x,y) or z(FX,x,y))]; rx=[x for x in xs if z(R,x,y)]
    if not fx: continue
    fw=min(fx); re=max([x for x in rx if x<fw] or [None]) if rx else None
    fz=z(F,fw+0.1,y) or z(FX,fw+0.1,y); rz=z(R,re-0.1,y) if re else None
    prof=[]
    for x in np.arange((re or fw-3),fw,0.2):
        gz=[v for v in [z(b,x,y) for b in G.values()] if v is not None]
        prof.append(round(fz-max(gz),2) if gz else None)
    print('y',y,'road_e',re and round(re,1),'foot_w',round(fw,1),'fz',fz,'rz',rz,'foot-ground',prof)

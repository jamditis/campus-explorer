import bpy, numpy as np, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=['Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','PB2_walk_lawn_fillet_UNVERIFIED','QQ_Richardson_paved_apron_UNVERIFIED']
BLD=[o.name for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('QP_Richardson','QT_Richardson_base_plinth','QU_G_floor')) or o.name.startswith('MO Health Drop-In Center walls'))]
WK=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('QS_footway','QT_soil_edge','QW_footway','QW_soil_edge'))]
B={n:bvh(bpy.data.objects[n]) for n in G+BLD+WK}
xs=np.arange(50,92,0.5); ys=np.arange(238,330,0.5)
out={n:np.full((len(ys),len(xs)),np.nan) for n in G}
bld=np.zeros((len(ys),len(xs)),bool); bldz=np.full((len(ys),len(xs)),np.nan)
walk=np.full((len(ys),len(xs)),np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        for n in G:
            h=B[n].ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if h[0] is not None: out[n][j,i]=h[0].z
        for n in BLD:
            h=B[n].ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if h[0] is not None: bld[j,i]=True
        for n in WK:
            h=B[n].ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if h[0] is not None: walk[j,i]=h[0].z if np.isnan(walk[j,i]) else max(walk[j,i],h[0].z)
np.savez(f'{R}/data/wt/cov_probe.npz',xs=xs,ys=ys,bld=bld,walk=walk,names=np.array(G),**{f'z{k}':out[n] for k,n in enumerate(G)})
# boundary edges of RZ2 and QW near tile
rep={'BLD':BLD,'WK':WK}
for n in ('RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'):
    o=bpy.data.objects[n]; me=o.data; cnt={}
    for p in me.polygons:
        for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
    bv=set()
    for ek,c in cnt.items():
        if c==1: bv.update(ek)
    pts=[o.matrix_world@me.vertices[i].co for i in bv]
    rep[n]=[[round(p.x,2),round(p.y,2),round(p.z,3)] for p in pts if 50<=p.x<=95 and 238<=p.y<=330]
# MO walls and plinth bottoms
for n in BLD:
    o=bpy.data.objects[n]; vs=[o.matrix_world@v.co for v in o.data.vertices]; rep['zmin_'+n]=round(min(v.z for v in vs),3)
json.dump(rep,open(f'{R}/data/wt/probe2.json','w'),indent=1); print('DONE')

import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
keep={'Terrain_LiDAR_DTM_1m','WS110_ground_patch_S_of_y-249_DTM2023_1m_lawn_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt','Context_skirt_3DEP_ortho_4km'}
bpy.data.batch_remove([o for o in bpy.data.objects if o.name not in keep])
dg=bpy.context.evaluated_depsgraph_get()
def bv(n,ev):
    o=bpy.data.objects[n]
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); e.to_mesh_clear()
    else:
        bm=bmesh.new(); bm.from_mesh(o.data)
    bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
T={'terrE':bv('Terrain_LiDAR_DTM_1m',True),'terrO':bv('Terrain_LiDAR_DTM_1m',False),'patch':bv('WS110_ground_patch_S_of_y-249_DTM2023_1m_lawn_UNVERIFIED',False),'apronE':bv('WS60_terrain_edge_apron_LiDAR_to_skirt',True),'skirtE':bv('Context_skirt_3DEP_ortho_4km',True)}
for y in (-246,-248,-249.2,-249.8,-250.5,-252):
    for x in (-265,-258,-235,-228,-220):
        r=[]
        for k,t in T.items():
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; r.append('%s=%s'%(k,round(h.z,2) if h else '-'))
        print('PB110',x,y,' '.join(r))

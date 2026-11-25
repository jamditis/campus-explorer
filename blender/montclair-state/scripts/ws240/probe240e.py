import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
pts=[(-352,-40),(-345,-35),(-380,-20),(-385,5),(-330,-60),(-360,40),(-20,1110),(-30,1090),(0,1060),(-60,1100)]
res=[]
for n in ['Terrain_LiDAR_DTM_1m','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam','M3a_north_LiDAR_DTM_1m_ext_y','Context_skirt_3DEP_ortho_4km','WS68_RHD_ground_northDTM (no']:
    o=next((x for x in bpy.data.objects if x.name.startswith(n)),None)
    if not o: continue
    for m in o.modifiers: m.show_viewport=m.show_render
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
    print('P240E',o.name[:30],[(p,round(t.ray_cast(Vector((p[0],p[1],300)),Vector((0,0,-1)))[0].z,2) if t.ray_cast(Vector((p[0],p[1],300)),Vector((0,0,-1)))[0] else None) for p in pts],flush=True)

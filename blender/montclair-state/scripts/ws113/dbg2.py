import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; px=bpy.data.objects['WS113_paving_tops_proxy']
B=BVHTree.FromPolygons([v.co[:] for v in px.data.vertices],[p.vertices[:] for p in px.data.polygons])
dg=bpy.context.evaluated_depsgraph_get()
for on in (True,False):
    t.modifiers['WS113_paving_edge_grade'].show_viewport=on; dg.update()
    me=t.evaluated_get(dg).to_mesh(); c=0
    print('P113 on',on,'verts',len(me.vertices),'faces',len(me.polygons))
    for v in me.vertices:
        if -241<v.co.x<-234 and -246<v.co.y<-235:
            h=B.ray_cast(Vector((v.co.x,v.co.y,300)),Vector((0,0,-1)),400)
            if h[0] and c<12: print('P113 v %.2f %.2f z %.3f pz %.3f'%(v.co.x,v.co.y,v.co.z,h[0].z)); c+=1
    t.evaluated_get(dg).to_mesh_clear()

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
cam=bpy.data.objects['QP_CAM_closeup_richardson_S_tower']; sc.camera=cam
sc.render.resolution_x=1024; sc.render.resolution_y=576
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world
tr,br,bl,tl=[M@v for v in fr]; o=M.translation
for (px,py) in ((20,160),(10,150),(30,170),(95,150),(225,125)):
    u=px/1024; v=1-py/576
    p=tl+(tr-tl)*u+(bl-tl)*(1-v)
    ok,loc,n,i,ob,m=sc.ray_cast(dg,o,(p-o).normalized())
    print('HIT',(px,py),ok and [round(c,2) for c in loc],ob.name if ok else None,ok and [round(c,2) for c in n], ok and ob.material_slots[ob.data.polygons[i].material_index].name if ok and ob.type=='MESH' and len(ob.data.polygons)>i else '')
# ground under footprint
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for (x,y) in ((74.2,239.5),(80.4,292.9),(84,264),(75,240.0),(80,293.5)):
    ok,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
    print('DOWN',(x,y),ok and round(loc.z,2),ob.name if ok else None)
for nm in ('Footpaths_OSM',):
    ob=bpy.data.objects.get(nm); print(nm, ob and len(ob.data.vertices))

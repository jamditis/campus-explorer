import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
import sys; sys.path.insert(0,'../ws5'); import cams; cams.CAMS={'WS10_CAM_oblique_cole_morehead_walk_from_S':((-60,-92,168),(-64,-54,135),26)}; cams.ensure(sc); sc.render.resolution_x=1280; sc.render.resolution_y=720; bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['WS10_CAM_oblique_cole_morehead_walk_from_S']
# camera frame
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
tr,br,bl,tl=[mw@v for v in fr]; o=mw.translation
W,H=1024,576
for px,py in [(300,440),(340,448),(250,420),(380,460),(200,400),(130,375)]:
    u=px/W; v=py/H
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    d=(p-o).normalized()
    r=sc.ray_cast(dg,o,d)
    print('PX',px,py,[round(x,2) for x in r[1]],r[4].name if r[0] else None,flush=True)

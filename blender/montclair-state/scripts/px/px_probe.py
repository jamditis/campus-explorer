import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['PV_CAM_closeup_dickson_north_toprow']; sc.camera=cam
print('CAM',tuple(round(x,2) for x in cam.location), tuple(round(x,3) for x in cam.matrix_world.to_3x3()@Vector((0,0,-1))))
from bpy_extras.object_utils import world_to_camera_view
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
tr,tl=[mw@fr[0],mw@fr[3]]; br,bl=mw@fr[1],mw@fr[2]
for (fx,fy) in [(0.2,0.05),(0.35,0.08),(0.5,0.14),(0.6,0.2),(0.66,0.24),(0.7,0.28),(0.72,0.35),(0.75,0.4),(0.3,0.2),(0.5,0.25)]:
    top=tl.lerp(tr,fx); bot=bl.lerp(br,fx); p=top.lerp(bot,fy)
    hit,loc,n,fi,o,_=sc.ray_cast(dg,cam.location,(p-cam.location).normalized())
    print('PROBE',fx,fy,hit and o.name, hit and tuple(round(x,2) for x in loc), hit and tuple(round(x,2) for x in n))

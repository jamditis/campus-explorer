import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['WS31_CAM_eye_dock_apron_from_E']
from bpy_extras.object_utils import world_to_camera_view
fr=cam.data.view_frame(scene=sc)  # local frame corners
tr,br,bl,tl=[cam.matrix_world@v for v in fr]
o=cam.matrix_world.translation
for (u,v) in [(0.85,0.5),(0.75,0.5),(0.95,0.48),(0.65,0.47),(0.9,0.55)]:
    p=bl+(br-bl)*u+(tl-bl)*v
    d=(p-o).normalized(); h=sc.ray_cast(dg,o,d)
    print('HIT',u,v,h[4].name if h[0] else None, tuple(round(c,2) for c in h[1]) if h[0] else None)

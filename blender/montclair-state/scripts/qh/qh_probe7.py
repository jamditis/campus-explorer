import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['QE_CAM_eye_ccis_east']; dg=bpy.context.evaluated_depsgraph_get()
sc.render.resolution_x=1024; sc.render.resolution_y=576
fr=cam.data.view_frame(scene=sc); M=cam.matrix_world; o=M.translation
def ray(u,v):
    # fr: tr, br, bl, tl in camera space
    tr,br,bl,tl=[M@p for p in fr]
    p=bl+(br-bl)*u+(tl-bl)*v; d=(p-o).normalized(); r=sc.ray_cast(dg,o,d)
    return (r[4].name,tuple(round(c,1) for c in r[1]),r[3]) if r[0] else None
for name,(u,v) in {('d%d_%d'%(a,b)):(0.024+0.093*k+0.004*b, 0.896-0.566*k) for a,k in enumerate([0.1,0.3,0.5,0.7,0.9]) for b in (-2,-1,0,1,2)}.items():
    print('P',name,ray(u,v))
print('CAM',tuple(round(c,1) for c in o))

import math
print('ROT',tuple(round(math.degrees(a),1) for a in cam.rotation_euler),cam.rotation_mode,cam.data.lens,cam.data.shift_y)

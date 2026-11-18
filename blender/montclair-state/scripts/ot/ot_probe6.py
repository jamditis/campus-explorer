import bpy
from mathutils import Vector
scn=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def ray(camn,px,py,W=768,H=432):
    cam=bpy.data.objects[camn]; fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=scn)]; o=cam.matrix_world.translation
    tl,tr,br,bl=fr[3],fr[0],fr[1],fr[2]; p=bl+(br-bl)*(px/W)+(tl-bl)*(1-py/H)
    r=scn.ray_cast(dg,o,(p-o).normalized(),distance=900)
    print('PX',camn[:12],px,py, r[0] and (r[4].name,[round(x,1) for x in r[1]], r[4].parent and r[4].parent.name, [c.name for c in r[4].users_collection][:2]))
for a in [('OR_CAM_eye_CELS_skirt_windows_base_course',630,165),('OR_CAM_eye_CELS_skirt_windows_base_course',608,208),('OR_CAM_eye_CELS_skirt_windows_base_course',700,230),('OR_CAM_eye_CELS_skirt_windows_base_course',600,240),
          ('OQ_CAM_eye_calcia_skirt_windows',120,195),('OQ_CAM_eye_calcia_skirt_windows',157,198),('OQ_CAM_eye_calcia_skirt_windows',60,215),('OQ_CAM_eye_calcia_skirt_windows',30,250)]: ray(*a)

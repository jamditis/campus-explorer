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
for name,(u,v) in {'tower_mid':(0.6,0.5),'tower_leftedge':(0.505,0.6),'tower_rightedge':(0.70,0.6),'tower_top':(0.6,0.97),'fascia_left':(0.06,0.5),'fascia_low':(0.11,0.33),'leftwall_top':(0.3,0.86),'leftwall_mid':(0.3,0.6),'rightwall_top':(0.85,0.73),'rightwall_mid':(0.85,0.55),'rightfin':(0.95,0.5),'leftband':(0.3,0.31),'base':(0.3,0.2)}.items():
    print('P',name,ray(u,v))
print('CAM',tuple(round(c,1) for c in o))

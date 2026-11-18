import bpy,os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
exec(open('scripts/we/we_render.py').read().split('if os.environ.get(\'SAVECAM\')')[0])
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
cam=O[os.environ.get('CAM','WE_CAM_closeup_stone_footway_junction_from_SE')]
CAMP=os.environ.get('CAMP')
if CAMP:
    from mathutils.bvhtree import BVHTree
    px,py,tx,ty=[float(v) for v in CAMP.split(',')]
sc.render.resolution_x=1280; sc.render.resolution_y=720
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl in cam space
tr,br,bl,tl=fr
for (u,v) in [tuple(float(a) for a in p.split(':')) for p in os.environ['PIX'].split(',')]:
    # u,v in 0..1 from top-left
    top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; pt=top+(bot-top)*v
    d=(cam.matrix_world.to_3x3()@pt).normalized(); o=cam.matrix_world.translation
    h=sc.ray_cast(dg,o,d)
    print('PIX',u,v,h[0] and (tuple(round(c,2) for c in h[1]),h[4].name,round(h[2].z,2)),flush=True)

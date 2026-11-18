# pz: closer camera on the NW step corner of the wing coping (corner cover, joints, stain, seams). REVERT=1 removes it.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; N='PZ_CAM_closeup_dickson_wing_nw_corner'
if N in bpy.data.objects:
    o=bpy.data.objects[N]; c=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(c); print('REVERTED',N)
if not REV:
    c=bpy.data.cameras.new(N); c.lens=35; o=bpy.data.objects.new(N,c)
    o.location=Vector((-185.0,166.5,155.6)); d=Vector((-176.9,158.6,151.6))-o.location
    o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['PV_CAM_closeup_dickson_north_toprow'].users_collection[0].objects.link(o); print('PZ_CAM added')

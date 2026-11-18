# py: close-up camera on the new wing parapet coping (NW corner, slightly above the roofline). REVERT=1 removes it.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; N='PY_CAM_closeup_dickson_wing_coping'
if N in bpy.data.objects:
    o=bpy.data.objects[N]; c=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(c); print('REVERTED',N)
if not REV:
    c=bpy.data.cameras.new(N); c.lens=35; o=bpy.data.objects.new(N,c)
    o.location=Vector((-192.0,171.0,157.2)); d=Vector((-178.0,156.0,152.3))-o.location
    o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    bpy.data.objects['PV_CAM_closeup_dickson_north_toprow'].users_collection[0].objects.link(o); print('PY_CAM added')

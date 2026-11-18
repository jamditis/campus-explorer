# pw: close-up camera on Dickson west windows showing the blinds/curtains through the glass. REVERT=1 removes it.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CAMS={'PW_CAM_closeup_dickson_west_blinds':((-191.0,98.5,139.2),(-181.0,95.5,141.2),40)}
for N in CAMS:
    if N in bpy.data.objects:
        o=bpy.data.objects[N]; d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d); print('REVERTED_PW_CAM',N)
if not REV:
    for N,(loc,tgt,lens) in CAMS.items():
        loc=Vector(loc); d=bpy.data.cameras.new(N); d.lens=lens; o=bpy.data.objects.new(N,d); o.location=loc
        o.rotation_euler=(Vector(tgt)-loc).to_track_quat('-Z','Y').to_euler()
        bpy.data.objects['PE_CAM_eye_dickson_west'].users_collection[0].objects.link(o); print('PW_CAM',N)

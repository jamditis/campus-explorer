# pv2: close-up camera on recessed Dickson west windows (oblique, to show reveal depth). REVERT=1 removes it.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CAMS={'PV2_CAM_closeup_dickson_west_recess':((-188.0,104.0,139.0),(-181.0,94.0,140.5),35)}
for N in CAMS:
    if N in bpy.data.objects:
        o=bpy.data.objects[N]; d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d); print('REVERTED_PV2_CAM',N)
if not REV:
    for N,(loc,tgt,lens) in CAMS.items():
        loc=Vector(loc); d=bpy.data.cameras.new(N); d.lens=lens; o=bpy.data.objects.new(N,d); o.location=loc
        o.rotation_euler=(Vector(tgt)-loc).to_track_quat('-Z','Y').to_euler()
        bpy.data.objects['PE_CAM_eye_dickson_west'].users_collection[0].objects.link(o); print('PV2_CAM',N)

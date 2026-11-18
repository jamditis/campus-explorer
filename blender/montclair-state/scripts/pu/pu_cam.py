# pu: close-up camera on the Dickson west windows (REVERT=1 removes it)
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; CN='PU_CAM_closeup_dickson_west_windows'
if CN in bpy.data.objects:
    o=bpy.data.objects[CN]; cd=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(cd); print('REVERTED_PU_CAM')
if not REV:
    cd=bpy.data.cameras.new(CN); cd.lens=35; o=bpy.data.objects.new(CN,cd)
    ref=bpy.data.objects['PE_CAM_eye_dickson_west']; ref.users_collection[0].objects.link(o)
    o.location=Vector((-190.5,91.0,139.6)); d=Vector((-181.2,101.5,142.8))-o.location
    o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); print('PU_CAM',CN)

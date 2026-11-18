# qc: close-up camera on the new Calcia west corner-bay openings. REVERT=1 removes it. UNVERIFIED framing only.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; CN='QC_CAM_closeup_calcia_west_cornerbay'
if CN in bpy.data.objects:
    o=bpy.data.objects[CN]; d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d); print('REVERTED_QC_CAM')
if not REV:
    tgt=Vector((-105.75,199.6,143.4)); n=Vector((-0.998,0.062,0)); side=Vector((0.062,0.998,0))
    loc=tgt+n*9+side*-2.5+Vector((0,0,1.0))
    cd=bpy.data.cameras.new(CN); cd.lens=30; o=bpy.data.objects.new(CN,cd)
    bpy.data.objects['PV_CAM_closeup_dickson_north_toprow'].users_collection[0].objects.link(o); o.location=loc
    o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); print('QC_CAM',tuple(round(x,2) for x in loc))

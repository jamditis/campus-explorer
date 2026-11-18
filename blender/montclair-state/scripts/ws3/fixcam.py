import bpy
from mathutils import Vector
o=bpy.data.objects['WS3_CAM_closeup_cole_plaza_from_S']
o.name='WS3_CAM_closeup_cole_plaza_from_NW'; o.data.name=o.name
loc=Vector((-124,-33,143.0)); tgt=Vector((-107,-47,134.2))
o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); o.data.lens=30
bpy.ops.wm.save_mainfile(); print('SAVED')

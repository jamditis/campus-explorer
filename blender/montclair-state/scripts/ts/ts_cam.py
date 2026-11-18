# ts close-up cam over the skirt/far-field seam east of campus. REVERT=1 removes it.
import bpy,os
from mathutils import Vector
N='TS_CAM_closeup_skirt_edge_E'
o=bpy.data.objects.get(N)
if o: d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
if os.environ.get('REVERT')!='1':
    c=bpy.data.cameras.new(N); c.lens=50; c.clip_end=6000
    o=bpy.data.objects.new(N,c); bpy.context.scene.collection.objects.link(o)
    o.location=(120,300,190); dv=Vector((520,330,95))-o.location
    o.rotation_euler=dv.to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_mainfile(); print('TSCAM done')

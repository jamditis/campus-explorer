import bpy, os, sys
from mathutils import Vector
N='ON_CAM_closeup_schmitt_SSW_corner_window_infill'; COL='ON_Schmitt_shard_fix_wall_infill_20261031on'
o=bpy.data.objects.get(N)
if o: d=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(d)
if os.environ.get('REVERT')!='1':
    cd=bpy.data.cameras.new(N); cd.lens=35; c=bpy.data.objects.new(N,cd)
    col=bpy.data.collections.get(COL) or bpy.data.collections.new(COL)
    if COL not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    col.objects.link(c); c.location=(-13.6,105.5,143.0)
    c.rotation_euler=(Vector((-15.7,117.1,146.8))-c.location).to_track_quat('-Z','Y').to_euler()
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')

import bpy, os
from mathutils import Vector
exec(compile(open('scripts/pz/pz_main.py').read(),'pz_main','exec'))
for N,loc,tg in (('ZZ_DBG_corner',(-178.6,162.0,153.6),(-176.65,159.75,152.85)),('ZZ_DBG_corner2',(-175.0,162.5,152.2),(-176.65,159.75,152.85))):
    c=bpy.data.cameras.new(N); c.lens=50; o=bpy.data.objects.new(N,c); o.location=Vector(loc)
    o.rotation_euler=(Vector(tg)-o.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/pz_test.blend',copy=True); print('DBG saved')

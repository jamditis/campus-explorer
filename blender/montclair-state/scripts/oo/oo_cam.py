# oo cameras: oblique over the re-draped walks NE of Schmitt (same pose as om's test cam) + eye-level on the re-draped N walk.
import bpy, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OO_Schmitt_cams_20261031oo'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        d=ob.data; bpy.data.objects.remove(ob)
        if d and d.users==0: bpy.data.cameras.remove(d)
    bpy.data.collections.remove(c)
if not REV:
    c=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(c)
    for name,loc,tgt,lens in [('OO_CAM_oblique_redraped_walks_NNE_of_schmitt',(75,215,142),(38,180,135),24),
                              ('OO_CAM_eye_redraped_walk_N_of_schmitt',(52,196,133.2),(20,176,134.6),28)]:
        d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); c.objects.link(o)
        o.location=Vector(loc); o.rotation_euler=(Vector(tgt)-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=lens
    L=bpy.data.objects.get('Lamp_acorn_050')
    if L:
        b=L.matrix_world.translation.copy()
        name='OO_CAM_closeup_redraped_walk_lamp_050'
        d=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,d); c.objects.link(o)
        o.location=b+Vector((-4.5,-5.0,1.5)); o.rotation_euler=((b+Vector((0,0,0.9)))-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=30
print('cams', 'removed' if REV else 'added')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

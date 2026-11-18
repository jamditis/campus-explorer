import bpy, mathutils
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
cam('OAT_2F_counter_prints',(1.6,11.4,143.3),(1.6,13.9,143.2),24)
exec(open('scripts/oa/oa_render.py').read())

import bpy, mathutils
exec(open('scripts/ny/ny_build.py').read())
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
cam('NYT_C',(6.4,15.0,138.95),(1.5,16.6,138.55),26)
cam('NYT_D',(4.4,16.6,138.9),(2.9,17.86,139.4),24)
exec(open('scripts/ny/ny_render.py').read())

import bpy, mathutils
exec(open('scripts/ny/ny_build.py').read())
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
cam('NYT_A',(6.4,15.0,138.9),(1.5,16.4,138.3),26)
cam('NYT_B',(6.2,17.6,139.0),(2.6,15.0,138.25),26)
exec(open('scripts/ny/ny_render.py').read())

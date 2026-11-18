import bpy, mathutils
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
cam('NYT_E',(6.4,15.0,138.95),(1.5,17.2,138.45),26)
cam('NYT_F',(6.45,14.5,138.9),(1.5,17.0,138.42),24)
exec(open('scripts/ny/ny_render.py').read())

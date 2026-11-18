import bpy, mathutils
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
cam('NZT_board',(2.6,16.0,139.1),(2.6,17.9,139.15),35)
cam('NZT_proj',(4.2,15.0,140.2),(3.0,16.6,140.5),30)
exec(open('scripts/ny/ny_render.py').read())

import bpy, math, sys
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws108/eaves108.py').read()); exec(open('/workspace/nj-scenes/montclair-state/scripts/ws108/winfix108.py').read())
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.display.shading.color_type='MATERIAL'; sc.display.shading.light='STUDIO'
sc.render.resolution_x=1200; sc.render.resolution_y=800
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.lens=35
for nm,(p,t) in {'E':((-140,-215,165),(-185,-188,132)),'SW':((-235,-250,150),(-195,-195,132))}.items():
    cam.location=p; d=Vector(t)-Vector(p); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.render.filepath='/workspace/nj-scenes/montclair-state/prep/ws108_Chapin_eaves/check108b_%s.png'%nm; bpy.ops.render.render(write_still=True)

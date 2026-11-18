import bpy, os
from mathutils import Vector
sc=bpy.context.scene; sc.render.engine='BLENDER_WORKBENCH'; sc.render.resolution_x=1100; sc.render.resolution_y=700
sc.display.shading.light='STUDIO'; sc.display.shading.color_type='MATERIAL'; sc.display.shading.show_shadows=True; sc.display.shading.show_cavity=True
def cam(name,loc,tgt,lens=28):
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_end=2000; o=bpy.data.objects.new(name,c); sc.collection.objects.link(o)
    o.location=loc; d=Vector(tgt)-Vector(loc); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); return o
for n,l,t in (('ob',(-232,-212,133),(-213,-195,124)),('eye',(-224,-198.8,124.7),(-210,-198.5,125.2))):
    sc.camera=cam(n,l,t); sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/test/ws117_wb_%s.png'%n; bpy.ops.render.render(write_still=True)

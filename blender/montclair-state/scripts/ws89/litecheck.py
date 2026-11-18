import bpy,math,os
from mathutils import Vector
sc=bpy.context.scene
for n in ('Plaza long arched wall',):
    with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d):
        d.objects=[x for x in s.objects if x.startswith(n) or x.startswith('WS88_Cole_statue')]
    for o in d.objects: sc.collection.objects.link(o)
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sun.data.energy=4; sun.rotation_euler=(math.radians(50),0,math.radians(200)); sc.collection.objects.link(sun)
sc.world=bpy.data.worlds.new('w'); sc.world.color=(0.6,0.7,0.9)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
def look(loc,tgt):
    cam.location=loc; d=Vector(tgt)-Vector(loc); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.cycles.device='CPU'; sc.render.resolution_x=900; sc.render.resolution_y=500
for nm,loc,tgt in (('obl',(-200,-108,140),(-180,-84,129)),('eye',(-190,-95,130.8),(-180,-84,129.4))):
    look(loc,tgt); sc.render.filepath=f'/workspace/nj-scenes/montclair-state/renders/test/ws89_steps_lite_{nm}.png'; bpy.ops.render.render(write_still=True)

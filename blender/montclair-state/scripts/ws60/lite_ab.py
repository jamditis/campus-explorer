import bpy,os
from mathutils import Vector
N=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (s,d): d.objects=list(N)
sc=bpy.context.scene
for o in list(sc.objects): bpy.data.objects.remove(o)
for o in d.objects: sc.collection.objects.link(o)
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=4; sun.rotation_euler=(0.9,0.2,2.2); sc.collection.objects.link(sun)
w=bpy.data.worlds.new('W'); sc.world=w; w.color=(0.45,0.5,0.55)
c=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(c); sc.camera=c
c.location=Vector((150,330,150)); c.rotation_euler=(Vector((175,230,122))-c.location).to_track_quat('-Z','Y').to_euler(); c.data.lens=35; c.data.clip_end=5000
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.render.resolution_x=960; sc.render.resolution_y=540; sc.render.image_settings.file_format='JPEG'
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/test/20261111_ws60_Nedge_before.jpg'; bpy.ops.render.render(write_still=True); print('WROTE b')
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/data/ws60/apron_uv.blend',link=False) as (s,d): d.objects=list(s.objects)
for o in d.objects: sc.collection.objects.link(o)
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/test/20261111_ws60_Nedge_after.jpg'; bpy.ops.render.render(write_still=True); print('WROTE a')

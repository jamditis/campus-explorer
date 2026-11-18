import bpy,os,runpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=['MID_street_tree_proto_20261015ag','MID_canopy_carpet_SW_far_crowns_wq2','MID_canopy_carpet_far_crowns_ai','Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=W+[n for n in s.objects if n.startswith('MID_stree_')]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/ws48/band_build.py')

import bpy
from mathutils import Vector
from datetime import datetime
sc=bpy.context.scene
for o in sc.objects:
    if o.name.startswith('MID_stree_'): pass
print('B48 MID_stree objs',sum(1 for o in sc.objects if o.name.startswith('MID_stree_')))
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun); sun.rotation_euler=(1.2,0,2.4); sun.data.energy=4
c=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(c); sc.camera=c
c.location=(-60,-40,175); c.data.lens=30; tgt=Vector((300,-450,90)); c.rotation_euler=(tgt-c.location).to_track_quat('-Z','Y').to_euler(); c.data.clip_end=5000
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.use_denoising=True; sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=60
sc.render.threads_mode='FIXED'; sc.render.threads=4; sc.render.image_settings.file_format='JPEG'
sc.render.filepath='/workspace/nj-scenes/montclair-state/renders/test/'+datetime.now().strftime('%Y%m%d-%H%M')+'_LITE_band_trees_ws48.jpg'
bpy.ops.render.render(write_still=True); print('B48 WROTE',sc.render.filepath)

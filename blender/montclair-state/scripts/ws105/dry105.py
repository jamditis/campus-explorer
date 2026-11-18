import bpy
A='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261113ws105.blend'
want=['Footpaths_OSM']
with bpy.data.libraries.load(A) as (s,d):
    names=[n for n in s.objects if n in want or n.startswith('WS103_CollegeAve_S_W_sidewalk') or n.startswith('WS99_bed_shrub_')]
    d.objects=names
    d.materials=[m for m in s.materials if m in ('WS3_Mulch_bark_dark_brown','WS35_black_painted_steel')]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('DRY appended',names)
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws105/build105.py').read(),'build105','exec'))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws105/dry105.blend')
print('DRY saved')

import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('WS27_','UA_CollegeAve','Terrain_LiDAR_DTM_1m','WS35_CollegeAve')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith(pre) and not n.startswith('Terrain_LiDAR_DTM_1m_hidden')]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws101/apply101b.py').read())

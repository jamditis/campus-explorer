import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('WS27_','WS35_CollegeAve','WS82_','WS83_','UA_CollegeAve','WS86_','WS81_','WS80_','WS94_','WS78_','WS98_','Terrain_LiDAR_DTM_1m')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith(pre) and not n.startswith('Terrain_LiDAR_DTM_1m_hidden')]
for o in d.objects:
    if o: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws101/apply101.py').read())

import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['UA_CollegeAve_spur_1557427669_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho','Terrain_LiDAR_DTM_1m']
for o in d.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws101/apply101c.py').read())

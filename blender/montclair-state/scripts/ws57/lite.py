import bpy
N=['Terrain_LiDAR_DTM_1m','Footpaths_OSM','Roads_OSM']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (s,d): d.objects=[n for n in N if n in s.objects]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws57/local_seat.py').read())

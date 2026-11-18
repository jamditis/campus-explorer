import bpy,os
N=['Terrain_LiDAR_DTM_1m','Footpaths_OSM','Roads_OSM']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (s,d): d.objects=[n for n in N if n in s.objects]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
src=open('/workspace/nj-scenes/montclair-state/scripts/ws57/local_seat.py').read().split('for n,cx,cy in SPOTS:')[0]
exec(src)
for n,cx,cy in SPOTS: print('L57 before',n,measure(n,cx,cy))
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws57/lift2.py').read())
for n,cx,cy in SPOTS: print('L57 after',n,measure(n,cx,cy))
if os.environ.get('SWEEP'): exec(open('/workspace/nj-scenes/montclair-state/scripts/ws43/sweep.py').read())

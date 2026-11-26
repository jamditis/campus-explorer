import bpy, os, json
S='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(S+'montclair_state_ws246a.blend') as (a,b): b.objects=[n for n in a.objects if n.startswith('M3b_north_LiDAR_DTM_1m')]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
os.environ['DRY']='1'; exec(open(S+'scripts/ws246/f246c.py').read()); os._exit(0)

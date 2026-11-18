import bpy, json, resource
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
L=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws149/treepave149.json'))
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=[r[0] for r in L]
for o in dst.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws149/limb149.py').read())
print("RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

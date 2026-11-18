import bpy, resource
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n=='Footpaths_OSM' or n.startswith('WS147_walk_E_of_forecourt')]
for o in dst.objects:
    for m in list(o.modifiers): o.modifiers.remove(m)
    bpy.context.scene.collection.objects.link(o)
print("RSS load",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, [o.name for o in dst.objects])
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws149/fix149_joints.py').read())
print("RSS end",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

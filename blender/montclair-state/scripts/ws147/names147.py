import bpy, resource
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend', link=False) as (src, dst):
    names=list(src.objects); mats=list(src.materials)
open('/workspace/nj-scenes/montclair-state/scripts/ws147/objnames.txt','w').write('\n'.join(names))
open('/workspace/nj-scenes/montclair-state/scripts/ws147/matnames.txt','w').write('\n'.join(mats))
print("N",len(names),len(mats),"RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

import bpy
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P, link=False) as (src,dst):
    names=list(src.objects)
open('/workspace/nj-scenes/montclair-state/scripts/ws151/objnames.txt','w').write('\n'.join(names))
print("N",len(names))

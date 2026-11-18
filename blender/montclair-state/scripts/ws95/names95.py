import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): names=list(s.objects)
open('/workspace/nj-scenes/montclair-state/scripts/ws95/names.txt','w').write("\n".join(names)); print("N",len(names))

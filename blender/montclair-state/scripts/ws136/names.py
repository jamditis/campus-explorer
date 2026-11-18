import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    ns=list(df.objects)
open('/workspace/nj-scenes/montclair-state/scripts/ws136/names.txt','w').write('\n'.join(ns)); print(len(ns))

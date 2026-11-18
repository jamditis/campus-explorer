import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    open('/workspace/nj-scenes/montclair-state/scripts/ws129/names.txt','w').write('\n'.join(df.objects))

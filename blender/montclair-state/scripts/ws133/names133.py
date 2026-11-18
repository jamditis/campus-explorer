import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (df,dt):
    open('/tmp/ws133_names.txt','w').write('\n'.join(df.objects))

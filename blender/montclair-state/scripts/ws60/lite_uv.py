import bpy
N=['Context_skirt_3DEP_ortho_4km']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (s,d): d.objects=list(N)
for o in d.objects: bpy.context.scene.collection.objects.link(o)
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/data/ws60/apron.blend',link=False) as (s,d): d.objects=list(s.objects)
for o in d.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws60/uv.py').read())
for o in list(bpy.data.objects):
    if not o.name.startswith('WS60'): bpy.data.objects.remove(o)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/data/ws60/apron_uv.blend'); print('UV60 saved')

import bpy,os
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
for o in bpy.data.objects:
    for m in o.modifiers: m.show_viewport=False
os.environ['DRY']='1'; exec(open('/workspace/nj-scenes/montclair-state/scripts/ws247/'+os.environ.get('FX','f247a.py')).read()); os._exit(0)

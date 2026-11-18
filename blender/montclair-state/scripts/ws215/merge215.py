import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws215/fix215a.py').read())
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws215a.blend', compress=True, copy=True)
print('MERGED215 saved', flush=True)

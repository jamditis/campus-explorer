import bpy, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws188/skirtoff188.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws189/poke189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
poke_restore(); hwm()
bpy.ops.wm.save_as_mainfile(filepath='/tmp/savetest189.blend',copy=True,compress=False); hwm(); print('SAVED',flush=True)

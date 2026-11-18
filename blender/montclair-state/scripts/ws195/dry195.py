import bpy, os
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
exec(open(S+'ws195/'+os.environ.get("SCR","fix195.py")+'').read())

import bpy, os
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
if os.environ.get('APPLY','1')=='1': exec(open(S+'ws193/fix193.py').read())
exec(open(S+'ws189/cutrend189.py').read())

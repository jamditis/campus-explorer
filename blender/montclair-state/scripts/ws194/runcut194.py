import bpy, os
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath=os.environ['FILE'])
exec(open(S+'ws189/cutrend189.py').read())

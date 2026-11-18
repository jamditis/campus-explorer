import bpy, os
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath=os.environ['FILE'])
for f in os.environ['PROBE'].split(): exec(open(S+f).read())

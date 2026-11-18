import bpy, resource
S='/workspace/nj-scenes/montclair-state/scripts/ws147/'
exec(open(S+'fix147_51.py').read())
exec(open(S+'fix147_52.py').read())
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws147a.blend',copy=True)
print("SAVED_WS147A RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
exec(open(S+'probe147.py').read())

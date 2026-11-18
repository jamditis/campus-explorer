import bpy, resource
S='/workspace/nj-scenes/montclair-state/scripts/ws148/'
exec(open(S+'fix148_53.py').read())
exec(open(S+'fix148_54.py').read())
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws148a.blend',copy=True)
print("SAVED_WS148A RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

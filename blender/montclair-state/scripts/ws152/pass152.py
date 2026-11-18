import bpy, resource
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/fix152.py').read())
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws152a.blend',copy=True)
print("SAVED_WS152A RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

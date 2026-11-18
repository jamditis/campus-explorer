import bpy, resource
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/fix152b.py').read())
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws152b.blend',copy=True)
print("SAVED_WS152B RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

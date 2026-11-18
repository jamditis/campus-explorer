import bpy, resource
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws151/fix151.py').read())
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws151a.blend',copy=True)
print("SAVED_WS151A RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
exec(open(M+'scripts/ws149/limb149.py').read())
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws151b.blend',copy=True)
print("SAVED_WS151B RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

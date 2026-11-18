import bpy, sys, resource
bpy.context.preferences.edit.use_global_undo=False
bpy.context.preferences.edit.undo_steps=0
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend', load_ui=False)
print('P47 loaded objs', len(bpy.data.objects), 'maxrss MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

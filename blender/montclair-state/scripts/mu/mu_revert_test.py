# Session mu REVERT test: delete the mu collection objects on an in-folder copy; expect 6,089 (= mt) objects. (Mesh trims are reverted by restoring montclair_state_pre_20261029mu.blend.)
import bpy
c=bpy.data.collections['MS_CCOM_gable_eave_returns_20261029mu']; k=len(c.objects)
for o in list(c.objects): bpy.data.objects.remove(o)
bpy.data.collections.remove(c)
print('REVERT removed',k,'COUNT',len(bpy.data.objects))

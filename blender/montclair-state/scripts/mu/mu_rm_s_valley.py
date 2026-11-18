# Session mu: the S valley flashing only found 3 crossing points at the back (w 18.9-19.3) and read as a stray light chip -> remove it (the S slab sits above the low main roof, no valley there).
import bpy
o=bpy.data.objects.get('CCOM gable valley flashing S (mu)')
if o: m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REMOVED S valley')
print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')

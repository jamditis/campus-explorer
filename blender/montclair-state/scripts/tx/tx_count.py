import bpy
print('COUNT',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),len(bpy.data.cameras),sum(1 for o in bpy.data.objects if o.get('tx_obj')))

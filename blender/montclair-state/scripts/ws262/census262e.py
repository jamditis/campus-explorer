# ws262 M4b verify (merge208 CHAIN, NO SAVE): libraries left, ID totals, scene object count, any ID whose name ends .001.. that
# came from the Sprague/Café Diem set, images with missing files.
import bpy, os
TAG='C262E'
print(TAG,'libs',[(l.name,l.users) for l in bpy.data.libraries],flush=True)
print(TAG,'objects',len(bpy.data.objects),'scene objs',len(bpy.context.scene.objects),'meshes',len(bpy.data.meshes),'mats',len(bpy.data.materials),'ng',len(bpy.data.node_groups),'imgs',len(bpy.data.images),'colls',len(bpy.data.collections),flush=True)
sp=[o.name for o in bpy.data.objects if o.library is None and o.name.startswith(('North_Sprague','North_CafeDiem','bv_','dN2_'))]
print(TAG,'sprague/cafe local objects',len(sp),flush=True)
miss=[(i.name,i.filepath) for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file and not os.path.exists(bpy.path.abspath(i.filepath))]
print(TAG,'images missing on disk',len(miss),miss[:6],flush=True)
os._exit(0)

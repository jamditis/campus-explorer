import bpy
g=sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH' and 'grass_points' in o.name)
print('REV_OBJCOUNT',len(bpy.data.objects),'grasspts',g,'libs',len(bpy.data.libraries),'mats',len(bpy.data.materials))

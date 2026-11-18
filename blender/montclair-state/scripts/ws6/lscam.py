import bpy
for o in bpy.data.objects:
  if o.type=='CAMERA' and any(k in o.name.lower() for k in ('cole','ws5','ws4')): print('CAMN',o.name)

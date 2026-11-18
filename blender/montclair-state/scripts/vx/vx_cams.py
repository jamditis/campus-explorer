import bpy
print('CAMS',[o.name for o in bpy.data.objects if o.type=='CAMERA' and ('Blanton' in o.name or 'east_dorms' in o.name)])

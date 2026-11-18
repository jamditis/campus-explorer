import bpy
c=bpy.data.collections['Shrub_Boxwood']
for o in c.all_objects: print('BX',o.name,o.hide_render,o.type,[m.type for m in o.modifiers], o.instance_type)
print('BXoff',tuple(c.instance_offset))
az=bpy.data.collections.get('Shrub_Azalea'); print('AZ',az)
for o in az.all_objects: print('AZO',o.name,o.hide_render,o.type,[m.type for m in o.modifiers])
for o in bpy.data.objects:
  if o.name.startswith('WS6_Boxwood'):
    o.instance_collection=az; o.name=o.name.replace('Boxwood','Azalea'); s=o.scale[0]*0.9; o.scale=(s,s,s)
bpy.ops.wm.save_mainfile(); print('SAVED')

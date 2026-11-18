import bpy
for o in bpy.data.objects:
  if o.name.endswith(('_0274','_0277')) or '0274' in o.name or '0277' in o.name: print('L',o.name,o.type,o.hide_render,o.data.name if o.data else '')

import bpy
for o in bpy.data.objects:
    if 'Environmental' in o.name or 'CELS' in o.name: print('M',o.name[:90],o.type,o.hide_render,[c.name for c in o.users_collection][:2])
print('LIBS',[(l.name,l.filepath) for l in bpy.data.libraries])

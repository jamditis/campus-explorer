import bpy
for m in bpy.data.materials:
    if 'sphalt' in m.name or 'JT_' in m.name[:3] or 'lot' in m.name.lower():
        print('SF_MAT',m.name,m.users)

import bpy
for o in bpy.data.objects:
    if 'chapin' in o.name.lower() and o.type=='MESH':
        print('CH',o.name[:60],len(o.data.polygons),[m.name for m in o.data.materials if m][:6])

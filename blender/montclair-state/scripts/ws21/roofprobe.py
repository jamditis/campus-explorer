import bpy
for o in bpy.data.objects:
    if o.name.startswith('Life Hall') and o.type=='MESH':
        me=o.data
        print('O',o.name,len(me.polygons),[m.name for m in me.materials if m],list(me.attributes.keys())[:12])
c=bpy.data.objects.get('Cole Hall roof') 
for o in bpy.data.objects:
    if 'Cole' in o.name and 'roof' in o.name.lower(): print('C',o.name,[m.name for m in o.data.materials if m],list(o.data.attributes.keys()), o.get('ws15'))

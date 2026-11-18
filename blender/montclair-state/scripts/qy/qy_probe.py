import bpy
c=bpy.data.collections['QX_StudentCenter_plaza_paving_UNVERIFIED']
for o in c.objects:
    d=o.data
    print('OBJ',o.name,o.type,len(d.vertices) if o.type=='MESH' else '',len(d.polygons) if o.type=='MESH' else '',[m.name for m in d.materials] if o.type=='MESH' else '', tuple(round(v,2) for v in o.location), list(d.attributes.keys()) if o.type=='MESH' else '')
for n in ('Footpaths_OSM','QS_Richardson_walks_UNVERIFIED','QW_Richardson_walks_ext_UNVERIFIED'):
    print(n, n in bpy.data.objects, n in bpy.data.collections)
print([c.name for c in bpy.data.collections if c.name.startswith(('QW','QS','QT'))])

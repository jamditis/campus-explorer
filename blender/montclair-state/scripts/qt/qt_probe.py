import bpy
for o in [o for o in bpy.data.collections['QS_Richardson_walks_UNVERIFIED'].objects if o.type=='MESH']:
    print('OBJ',o.name,len(o.data.polygons),[m.name for m in o.data.materials],[u.name for u in o.data.uv_layers])
m=bpy.data.objects['Footpaths_OSM'].material_slots[0].material
print('MAT',m.name,m.users)
for n in m.node_tree.nodes: print(' N',n.name,n.bl_idname,[ (i.name,[l.from_node.name for l in i.links]) for i in n.inputs if i.links])
for nm in ('soil','dirt','mud','Soil'):
    print([x.name for x in bpy.data.materials if nm.lower() in x.name.lower()][:10])

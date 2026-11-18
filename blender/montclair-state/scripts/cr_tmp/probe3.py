import bpy
o = bpy.data.objects['Alexander Kasser Theater walls']
print('ATTR', [(a.name, a.domain, a.data_type) for a in o.data.attributes])
mt = bpy.data.materials['Wall_stucco_mission']
print('ATTRN', [nd.attribute_name for nd in mt.node_tree.nodes if nd.type=='ATTRIBUTE'])
print('USERS', [ob.name for ob in bpy.data.objects if ob.type=='MESH' and 'Wall_stucco_mission' in [m.name for m in ob.data.materials if m]][:30])

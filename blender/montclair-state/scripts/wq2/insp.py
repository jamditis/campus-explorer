import bpy
for n in ['MID_canopy_carpet_far_crowns_ai','MID_canopy_carpet_near_crowns_ai','MID_canopy_carpet_near_trunks_ai','MID_canopy_carpet_far2_crowns_ai']:
  o=bpy.data.objects[n]; m=o.data
  print('O',n,len(m.vertices),len(m.polygons),[ (a.name,a.data_type,a.domain) for a in m.attributes],[ (md.name,md.node_group.name if md.type=='NODES' else '') for md in o.modifiers],[c.name for c in o.users_collection], list(o.matrix_world.translation))
  print('  v0',m.vertices[0].co[:], {a.name: (a.data[0].vector[:] if hasattr(a.data[0],'vector') else a.data[0].value) for a in m.attributes if a.domain=='POINT' and a.name!='position'})
ng=bpy.data.objects['MID_canopy_carpet_far_crowns_ai'].modifiers[0].node_group
print('NODES',[(nd.type,nd.name,getattr(nd,'data_type','')) for nd in ng.nodes])
for nd in ng.nodes:
  if nd.type in('INPUT_ATTRIBUTE','OBJECT_INFO','COLLECTION_INFO'): print(nd.name, getattr(nd,'attribute_name',''), [ (i.name, getattr(i,'default_value',None)) for i in nd.inputs])

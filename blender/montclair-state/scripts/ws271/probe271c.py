import bpy
ng=bpy.data.node_groups['WS86_grandstand_hump_to_DTM_lower_only']
for n in ng.nodes:
    print('P271C N',n.name,n.type,getattr(n,'operation',''),getattr(n,'interpolation_type',''),getattr(n,'data_type',''),[ (i.name,i.default_value if not hasattr(getattr(i,'default_value',None),'__len__') else '') for i in n.inputs if hasattr(i,'default_value') and not i.is_linked])
for l in ng.links:
    print('P271C L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)
m=bpy.data.objects['Terrain_LiDAR_DTM_1m'].modifiers
names=[x.name for x in m]; i=names.index('WS86_grandstand_hump_to_DTM_lower_only'); print('P271C order',i,len(names),names[i-2:i+4])
raise SystemExit(0)

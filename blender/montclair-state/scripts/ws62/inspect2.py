import bpy
ng=bpy.data.node_groups['MID_canopy_carpet_far_crowns_ai_GN']
for n in ng.nodes:
    vals={i.name:(tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
    extra={}
    for a in ('data_type','operation','domain','attribute_name' ):
        if hasattr(n,a): extra[a]=getattr(n,a)
    if n.type=='COLLECTION_INFO': extra['coll']=n.inputs[0].default_value.name if n.inputs[0].default_value else None
    if n.type=='OBJECT_INFO': extra['obj']=n.inputs[0].default_value.name if n.inputs[0].default_value else None
    print('N',n.name,n.type,extra,vals)
for l in ng.links: print('L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)
for nm in ('MID_canopy_carpet_far2_crowns_ai_GN','MID_canopy_carpet_near_crowns_ai_GN'):
    g=bpy.data.node_groups[nm]
    for n in g.nodes:
        if n.type in('COLLECTION_INFO','RANDOM_VALUE','SCALE_INSTANCES','MATH','OBJECT_INFO'):
            print(nm,n.name,[ (i.name,(tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked and not hasattr(i.default_value,'name')], getattr(n,'operation',''))
for c in bpy.data.collections:
    if 'canopy' in c.name.lower() or 'BL' in c.name: print('COLL',c.name,[o.name for o in c.objects])
for o in ['MID_canopy_carpet_proto_crown_ai','MID_canopy_carpet_proto_crown_broad_bl','MID_canopy_carpet_proto_crown_lumpy_bl']:
    ob=bpy.data.objects[o]; me=ob.data
    import mathutils
    xs=[v.co for v in me.vertices]
    print('PROTO',o,me.name,len(me.vertices),len(me.polygons),me.polygons[0].use_smooth,[min(c[i] for c in xs) for i in range(3)],[max(c[i] for c in xs) for i in range(3)],me.users,list(me.attributes.keys()))
m=bpy.data.materials['MID_canopy_carpet_leaf_ai'];nt=m.node_tree
for n in nt.nodes:
    vals={i.name:(tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
    print('M',n.name,n.type,getattr(n,'attribute_name',''),getattr(n,'data_type',''),getattr(n,'blend_type',''),vals)
for l in nt.links: print('ML',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)
for o in ['MID_canopy_carpet_far_crowns_ai','MID_canopy_carpet_far2_crowns_ai','MID_canopy_carpet_near_crowns_ai','MID_canopy_carpet_SW_far_crowns_wq2','MID_canopy_carpet_SW_near_crowns_wq2']:
    ob=bpy.data.objects[o]; print('PTS',o,list(ob.data.attributes.keys()),[ (c.name) for c in ob.users_collection])

import bpy
for mn in ['North_wall_Dickson_brick_buff','North_Dickson_brick_buff_plain','North_Dickson_brick_red_accent','Wall_stucco_mission']:
    m=bpy.data.materials.get(mn)
    if not m: print('MAT',mn,'missing');continue
    print('MAT',mn,[ (n.type, getattr(n,'from_instancer',None), [l.from_socket.name for i in n.inputs for l in i.links][:3]) for n in m.node_tree.nodes if n.type in('TEX_COORD','UVMAP','TEX_IMAGE','MAPPING','ATTRIBUTE','TEX_BRICK')])
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE': print('  IMG',n.image.name if n.image else None, n.image.filepath if n.image else '')
        if n.type=='ATTRIBUTE': print('  ATTR',n.attribute_name)
    for n in m.node_tree.nodes:
        for o in n.outputs:
            for l in o.links:
                if n.type in('TEX_COORD','UVMAP'): print('  LINK',n.type,o.name,'->',l.to_node.type,l.to_node.name)
o=bpy.data.objects.get('Dickson Hall walls') or bpy.data.objects.get('Dickson Hall')
if o: print('OBJ',o.name,'uv',[u.name for u in o.data.uv_layers],'attrs',[a.name for a in o.data.attributes][:20], 'polys',len(o.data.polygons), [ (s.link) for s in o.material_slots])
o=bpy.data.objects.get('Dickson Hall roof (LiDAR)')
if o: print('ROOF slots',[(s.link,s.material.name) for s in o.material_slots],'polys',len(o.data.polygons))

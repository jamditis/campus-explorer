import bpy
m=bpy.data.materials['PE_Calcia_brick_slot_windows_UNVERIFIED']
for n in m.node_tree.nodes:
    if n.type in('MATH','ATTRIBUTE','SEPXYZ','UVMAP','MAP_RANGE'):
        print('N',n.name,getattr(n,'operation',''),getattr(n,'attribute_name',''),getattr(n,'uv_map',''),[(i.links[0].from_node.name+'.'+i.links[0].from_socket.name) if i.is_linked else round(i.default_value,3) for i in n.inputs[:2]])
us=[o for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
for o in us:
    me=o.data; print('USER',o.name,len(me.polygons),[u.name for u in me.uv_layers],[a.name for a in me.attributes])
    si=[i for i,s in enumerate(o.material_slots) if s.material==m]
    k=0
    for p in me.polygons:
        if p.material_index in si and p.area>20 and k<3:
            k+=1; uv=me.uv_layers.active.data
            print(' F',p.index,round(p.area,1),[(tuple(round(c,2) for c in o.matrix_world@me.vertices[me.loops[l].vertex_index].co),tuple(round(c,2) for c in uv[l].uv)) for l in p.loop_indices][:4])

import bpy
for mn in ['hn_amphi_seat_stone_blocks','hn_amphi_riser_coursed_stone','io_amphi_aisle_stone']:
    m=bpy.data.materials[mn]; nt=m.node_tree
    print('=== MAT',mn, len(nt.nodes))
    for n in nt.nodes:
        ins=[]
        for i in n.inputs:
            if i.is_linked: ins.append(f"{i.name}<-{i.links[0].from_node.name}.{i.links[0].from_socket.name}")
            elif hasattr(i,'default_value') and i.enabled:
                try: v=tuple(round(x,3) for x in i.default_value)
                except TypeError: v=round(i.default_value,3) if isinstance(i.default_value,float) else i.default_value
                ins.append(f"{i.name}={v}")
        extra=''
        if n.bl_idname=='ShaderNodeUVMap': extra=f' uv={n.uv_map}'
        if n.bl_idname=='ShaderNodeAttribute': extra=f' attr={n.attribute_name}'
        if n.bl_idname=='ShaderNodeTexBrick': extra=f' off={n.offset} freq={n.offset_frequency} sq={n.squash} sqf={n.squash_frequency}'
        if n.bl_idname=='ShaderNodeMath' or n.bl_idname=='ShaderNodeVectorMath' or n.bl_idname=='ShaderNodeMix': extra=f' op={getattr(n,"operation",getattr(n,"blend_type",""))}'
        print(f"  {n.name} [{n.bl_idname}] lbl={n.label}{extra} :: "+'; '.join(ins))
users=[o for o in bpy.data.objects if o.type=='MESH' and any(s.material and s.material.name=='hn_amphi_seat_stone_blocks' for s in o.material_slots)]
for o in users:
    me=o.data; print('OBJ',o.name,len(me.vertices),len(me.polygons),[u.name for u in me.uv_layers],[a.name for a in me.attributes], [mod.type for mod in o.modifiers])

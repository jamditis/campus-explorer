import bpy
ng=bpy.data.node_groups['WU_skirt_under_richardson_reid']
print('NODES:')
for n in ng.nodes:
    extra=''
    if n.bl_idname=='ShaderNodeMath' or n.bl_idname=='ShaderNodeVectorMath' or n.bl_idname.startswith('FunctionNode') or 'Math' in n.bl_idname:
        extra=' op='+getattr(n,'operation','?')
        extra+=' ins='+str([(i.name, i.is_linked, None if not hasattr(i,'default_value') or not isinstance(getattr(i,'default_value',None),(int,float)) else round(i.default_value,3)) for i in n.inputs[:4]])
    if n.bl_idname=='GeometryNodeSetPosition':
        extra=' SETPOS'
    if n.bl_idname=='GeometryNodeRaycast':
        extra=' RAY mapping='+getattr(n,'mapping','?')+' data='+getattr(n,'data_type','?')
    print(f'  {n.bl_idname:40s} {n.name:30s}{extra}')
print('LINKS to/from Math / Set Position / Raycast / Compare / Attribute:')
care=set()
for n in ng.nodes:
    if any(k in n.name or k in n.bl_idname for k in ('Math','Set Position','Raycast','Compare','Attribute','Boolean','Scale','Offset')):
        care.add(n)
for l in ng.links:
    if l.from_node in care or l.to_node in care:
        print(f'  {l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}')

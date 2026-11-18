import bpy
for o in bpy.data.objects:
    if 'Stone' in o.name and o.type=='MESH':
        bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
        print('OBJ',o.name,o.hide_render,[m.name if m else None for m in o.data.materials],len(o.data.polygons),
              [round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)])
m=bpy.data.materials.get('TM_dorm_wall_streaked_UNVERIFIED')
if m:
    for n in m.node_tree.nodes: print('N',n.name,n.type, getattr(n,'attribute_name',''))
    for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
print('NOBJ',len(bpy.data.objects))
for o in bpy.data.objects:
    if o.type=='CAMERA' and o.name[:3] in ('TI_','TJ_','TK_','TL_','TM_','TN_','TP_'): print('CAM',o.name,[round(v,1) for v in o.location])

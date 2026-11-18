import bpy
for m in bpy.data.materials:
    if 'walk' in m.name.lower() and m.use_nodes:
        users=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
        print('MAT',m.name,'users',len(users),users[:4])
        if m.name.startswith('QT_walk') or 'concrete_joints' in m.name:
            for n in m.node_tree.nodes:
                extra=''
                if n.type=='TEX_IMAGE' and n.image: extra=f' img={n.image.name} {tuple(n.image.size)} interp={n.interpolation} proj={n.projection}'
                if n.type=='MIX': extra=f' blend={n.blend_type} fac={n.inputs[0].default_value if not n.inputs[0].is_linked else "linked"}'
                print('  N',n.name,n.type,n.label,extra)
            for l in m.node_tree.links:
                print('  L',l.from_node.name,l.from_socket.identifier,'->',l.to_node.name,l.to_socket.identifier)

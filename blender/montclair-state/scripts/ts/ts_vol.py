import bpy
w=bpy.context.scene.world; print('WVOL',w.node_tree.nodes['Output' if 'Output' in w.node_tree.nodes else 'World Output'].inputs['Volume'].is_linked if True else '')
for n in w.node_tree.nodes:
    if n.type=='OUTPUT_WORLD': print('WOUT',n.name,n.inputs['Volume'].is_linked, n.is_active_output)
for m in bpy.data.materials:
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.type in ('VOLUME_SCATTER','PRINCIPLED_VOLUME','VOLUME_ABSORPTION'):
                us=[o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots) and not o.hide_render]
                print('VOL',m.name,n.type,us[:5])
sc=bpy.context.scene; print('COMP',sc.use_nodes, [n.type for n in sc.node_tree.nodes] if sc.node_tree else None)

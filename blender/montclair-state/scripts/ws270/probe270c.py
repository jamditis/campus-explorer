import bpy
for o in [o for o in bpy.data.objects if o.name.startswith(('WS68_RHD_ground_northDTM','M3b_north_LiDAR'))]:
    for ms in o.material_slots:
        m=ms.material
        if not m or not m.node_tree: continue
        tc=[(n.type,[l.from_socket.name for l in n.outputs[0].links] if n.outputs else '') for n in m.node_tree.nodes if n.type in ('TEX_COORD','UVMAP','ATTRIBUTE','TEX_IMAGE','MAPPING','GEOMETRY')]
        links=[(l.from_node.type,l.from_socket.name,l.to_node.type) for l in m.node_tree.links if l.from_node.type in ('TEX_COORD','UVMAP','GEOMETRY','ATTRIBUTE')]
        print('P270C',o.name[:30],m.name,m.users,links,flush=True)
raise SystemExit(0)

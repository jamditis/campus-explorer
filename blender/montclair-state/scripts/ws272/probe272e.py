import bpy, os, sys
OB=bpy.data.objects
for nm in ('WS68_RHD_ground_northDTM','WS60_terrain_edge_apron'):
    o=[x for x in OB if x.name.startswith(nm)][0]
    print('P272E',o.name[:40],'mats',[m.name if m else None for m in o.data.materials],'uv',[u.name for u in o.data.uv_layers],'attrs',[a.name for a in o.data.attributes][:12],flush=True)
    for m in o.data.materials:
        if not m or not m.use_nodes: continue
        for n in m.node_tree.nodes:
            ex=''
            if n.type=='TEX_IMAGE': ex=n.image.name if n.image else ''
            if n.type in('UVMAP',): ex=n.uv_map
            if n.type=='ATTRIBUTE': ex=n.attribute_name
            print('P272E   ',m.name[:30],n.type,n.name[:25],ex,[l.from_node.type+'.'+l.from_socket.name for i in n.inputs for l in i.links][:4],flush=True)
sys.stdout.flush(); os._exit(0)

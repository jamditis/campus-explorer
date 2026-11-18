import bpy
for n in ('Dickson Hall walls','Calcia Hall walls'):
    w=bpy.data.objects[n]; me=w.data
    print('W',n,len(me.vertices),len(me.polygons),[u.name for u in me.uv_layers],[a.name for a in me.attributes],[m.name for m in me.materials], dict(w.items()).keys(), w.hide_render)
    for m in me.materials:
        if m and m.node_tree: print('  NODES',m.name,[ (nd.type,nd.label or nd.name) for nd in m.node_tree.nodes][:60])

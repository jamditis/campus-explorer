import bpy
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if n.startswith('WS68_RHD_ground')]
for o in to.objects:
    print('OBJ',o.name,len(o.data.vertices),[m.name for m in o.data.materials],o.matrix_world.translation[:])
    import mathutils
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; print('BB',min(p.x for p in bb),max(p.x for p in bb),min(p.y for p in bb),max(p.y for p in bb))
    print('UV',o.data.uv_layers.keys(), [m.name+':'+m.type for m in o.modifiers])
    for m in o.data.materials:
        for n in m.node_tree.nodes:
            ex=''
            if n.type=='TEX_IMAGE' and n.image: ex=n.image.filepath+' '+str(tuple(n.image.size))
            print(' N',n.name,n.type,n.label,ex)
        for l in m.node_tree.links: print(' L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

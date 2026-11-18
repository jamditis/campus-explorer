import bpy
o=[x for x in bpy.data.objects if x.name.startswith('Calcia') and 'roof' in x.name.lower()]
for r in o:
    me=r.data; print('ROOF',r.name,len(me.polygons),[m.name for m in me.materials],dict(r.items()) if len(r.keys())<12 else list(r.keys()),[a.name for a in me.attributes])
    import collections
    A=collections.Counter(); 
    for p in me.polygons:
        k=('steep' if p.normal.z<0.93 else 'flat', p.material_index); A[k]+=p.area
    print(' AREA',{k:round(v,1) for k,v in A.items()})
    for m in me.materials:
        if not m or not m.node_tree: continue
        for n in m.node_tree.nodes:
            ex=''
            if n.type in ('ATTRIBUTE',): ex=n.attribute_name
            if n.type=='NEW_GEOMETRY' or n.type=='TEX_COORD': ex='geo'
            if n.type in ('MATH','MAP_RANGE','MIX','ATTRIBUTE','NEW_GEOMETRY','SEPXYZ','VALTORGB','TEX_IMAGE'):
                print('  N',m.name,n.name,n.type,getattr(n,'operation',''),ex,[(l.to_node.name,l.to_socket.name) for l in n.outputs[0].links][:2] if n.outputs else '')

import bpy
for n in ('Footpaths_OSM',):
    o=bpy.data.objects[n]; me=o.data
    print('OBJ',n,len(me.vertices),len(me.polygons),[ (m.name,m.type,m.show_render) for m in o.modifiers],[m.name for m in me.materials],[a.name for a in me.attributes])
    for m in o.modifiers:
        if m.type=='NODES' and m.node_group:
            print(' NG',m.node_group.name,[ (nd.name,nd.type) for nd in m.node_group.nodes])
    import collections
    e=collections.Counter(len(p.vertices) for p in me.polygons); print(' polysizes',e.most_common(5))
    # edge lengths
    import statistics
    L=[ (me.vertices[a].co-me.vertices[b].co).length for a,b in (ed.vertices for ed in me.edges)]
    print(' edge len median',statistics.median(L),'max',max(L))
for m in bpy.data.objects['Footpaths_OSM'].data.materials:
    print('MAT',m.name,[ (n.name,n.type) for n in m.node_tree.nodes][:30])

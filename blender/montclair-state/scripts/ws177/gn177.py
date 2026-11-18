import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith('WS110_ground_patch')]
for o in b.objects:
    for m in o.modifiers:
        print('MOD',m.name,m.type, m.node_group.name if m.node_group else None)
        for k in m.keys():
            v=m[k]; print('  key',k,getattr(v,'name',v))
        for n in m.node_group.nodes:
            if n.type in ('OBJECT_INFO','COLLECTION_INFO','INPUT_OBJECT','INPUT_COLLECTION'): 
                print('  node',n.type,n.name,[ (i.name, getattr(i,'default_value',None) and getattr(i.default_value,'name',None)) for i in n.inputs], getattr(n,'object',None), getattr(n,'collection',None))
        for it in m.node_group.interface.items_tree: print('  iface',it.name,getattr(it,'socket_type',None))

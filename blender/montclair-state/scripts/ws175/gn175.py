import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS110_ground_patch','WS163_walk_back_lawn_lip_S'))]
for o in b.objects:
    print('OBJ',o.name,[ (m.name,m.type) for m in o.modifiers], [m.name for m in o.data.materials])
    for m in o.modifiers:
        if m.type=='NODES':
            ng=m.node_group; print(' NG',ng.name)
            for n in ng.nodes: print('  N',n.bl_idname,n.name,n.label, [ (i.name,getattr(i,'default_value',None) if not hasattr(getattr(i,'default_value',None),'__len__') else tuple(i.default_value)) for i in n.inputs if not i.is_linked][:6])
            for k,v in m.items(): print('  IN',k,v)

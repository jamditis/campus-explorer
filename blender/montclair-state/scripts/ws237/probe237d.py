import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Context_skirt_3DEP_ortho_4km']
o=b.objects[0]; print('P237D verts',len(o.data.vertices))
for m in o.modifiers:
    print('P237D MOD',m.name,m.type,m.show_render, m.node_group.name if m.type=='NODES' and m.node_group else '')
    if m.type=='NODES':
        for k in m.keys():
            v=m[k]; 
            try: v=v.name
            except Exception: pass
            print('P237D   ',k,v)
        for it in m.node_group.interface.items_tree:
            print('P237D   IF',getattr(it,'in_out',''),it.name,getattr(it,'identifier',''))
        for n in m.node_group.nodes:
            ex=''
            if n.type in('OBJECT_INFO','COLLECTION_INFO'):
                i=n.inputs[0]; ex=str(getattr(i,'default_value',None))
            print('P237D     N',n.name,n.type,ex)

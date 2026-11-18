import bpy
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('P113 verts',len(t.data.vertices),'vg',[g.name for g in t.vertex_groups][:30])
for m in t.modifiers:
    s=m.type
    if m.type=='NODES':
        ng=m.node_group; ins={}
        for it in ng.interface.items_tree:
            if getattr(it,'in_out',None)=='INPUT' and it.socket_type!='NodeSocketGeometry':
                try: ins[it.name]=m[it.identifier] if it.identifier in m.keys() else None
                except Exception as e: ins[it.name]='?'
        def fmt(v):
            try: return v.name
            except: return v
        print('P113 MOD',m.name,ng.name,m.show_render,{k:fmt(v) for k,v in ins.items()})
    else: print('P113 MOD',m.name,s,m.show_render)
print('P113 attrs',[a.name for a in t.data.attributes])

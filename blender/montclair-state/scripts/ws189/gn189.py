import bpy
for gname in ('WS163_skirt_under_normalave_W','WS167_skirt_under_Lot3N_W','WS172_skirt_under_frontyards_S_NormalAve_W.001'):
    g=bpy.data.node_groups[gname]; print('GROUP',gname,flush=True)
    for n in g.nodes:
        vals=[]
        for i in n.inputs:
            if not i.is_linked and hasattr(i,'default_value'):
                v=i.default_value
                try: v=tuple(round(x,3) for x in v)
                except TypeError: v=round(v,3) if isinstance(v,float) else (v.name if hasattr(v,'name') else v)
                vals.append((i.name,v))
        extra=getattr(n,'operation',None) or getattr(n,'data_type',None) or ''
        print(' N',n.name,n.bl_idname,extra,vals,flush=True)
    for l in g.links: print(' L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

import bpy,sys
m=bpy.data.materials[sys.argv[-1]]
for n in m.node_tree.nodes:
    vals=[]
    for i in n.inputs:
        if not i.is_linked and hasattr(i,'default_value'):
            v=i.default_value
            try: v=tuple(round(x,3) for x in v)
            except TypeError: v=round(v,3) if isinstance(v,float) else v
            vals.append((i.name,v))
    extra=getattr(n,'operation','') or getattr(n,'blend_type','') or getattr(n,'uv_map','')
    print('N',n.name,n.type,extra,vals)
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

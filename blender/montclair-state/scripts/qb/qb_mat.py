import bpy
m=bpy.data.materials['PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED']
print('USERS',m.users,[o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots)])
def dump(nt,ind=''):
    for n in nt.nodes:
        ins=[(i.name, tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if not i.is_linked and hasattr(i,'default_value')][:5]
        print(ind+'N',n.name,n.type,getattr(n,'operation',''),getattr(getattr(n,'node_tree',None),'name',''),ins)
    for l in nt.links: print(ind+'L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
dump(m.node_tree)

import bpy
m=bpy.data.materials['Wall_stucco_mission']
def dump(nt,ind=''):
    for nd in nt.nodes:
        ins=[(i.name, round(i.default_value,3) if isinstance(i.default_value,float) else '') for i in nd.inputs if not i.is_linked and hasattr(i,'default_value')]
        print('N',ind,nd.type,nd.name,nd.label,ins[:5], (nd.node_tree.name if nd.type=='GROUP' else ''))
    for l in nt.links: print('L',ind,l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
dump(m.node_tree)
print('USERS',[o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots)][:40])

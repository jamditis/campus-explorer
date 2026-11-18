import bpy
m=bpy.data.materials['PE_Calcia_skirt_brick_UNVERIFIED']
for n in m.node_tree.nodes:
    ins={i.name:(tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}
    print('N',n.name,n.type,getattr(n,'operation',''),ins, [ (l.from_node.name) for i in n.inputs for l in i.links])

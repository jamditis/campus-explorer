import bpy
m=bpy.data.materials['OV_Paving_concrete_walk_tone_UNVERIFIED']; nt=m.node_tree
for l in nt.links:
    if l.from_node.name in('Texture Coordinate','Separate XYZ','Math.024','Math.034','Math.035','Mix.001','Mix.002','Mix.006','OV_walk_tone'): print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for i in range(0,36):
    n=nt.nodes.get('Math.%03d'%i if i else 'Math')
    if n: print(n.name,n.operation,[round(x.default_value,4) for x in n.inputs if not x.links and hasattr(x,'default_value') and not hasattr(x.default_value,'__len__')])
for nn in ('Mix.001','Mix.002'):
    n=nt.nodes[nn]; print(nn,n.data_type,n.blend_type,[tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if i.enabled and not i.links])
print('users',[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)])

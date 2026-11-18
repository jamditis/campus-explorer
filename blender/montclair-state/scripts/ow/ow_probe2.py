import bpy
r=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; me=r.data; m=me.materials[0]
print('MAT',m.name,'mods',[(x.name,x.type) for x in r.modifiers])
for n in m.node_tree.nodes:
    if n.type=='ATTRIBUTE': print(' A',n.name,n.attribute_name,n.attribute_type,[(o.name,[(l.to_node.name,l.to_socket.name) for l in o.links]) for o in n.outputs if o.links])
for nm in ('Math.036','Map Range.002','RGB to BW','Mix.007','Mix.002','Mix.006'):
    n=m.node_tree.nodes[nm]; print(nm,getattr(n,'operation',''),[(i.name,round(i.default_value,3) if isinstance(i.default_value,float) else '') for i in n.inputs if not i.links and hasattr(i,'default_value')][:6])
n=m.node_tree.nodes['RGB to BW']; print('rgb2bw in',[(l.from_node.name,l.from_socket.name) for l in n.inputs[0].links])

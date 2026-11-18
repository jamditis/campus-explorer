import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F,link=False) as (s,d):
    d.objects=['MID_street_tree_proto_20261015ag']; cams=[o for o in s.objects if 'cole' in o.lower() and ('cam' in o.lower())]
print('P49 cams',cams[:40])
p=bpy.data.objects['MID_street_tree_proto_20261015ag']; m=p.data.materials[0] if p.data.materials else None
print('P49 mat',m and m.name)
if m and m.use_nodes:
    for n in m.node_tree.nodes:
        ins={i.name:(tuple(round(v,3) for v in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked and i.name in ('Base Color','Roughness','Color','Fac','Scale','Strength','Value')}
        print('P49 node',n.type,n.name,ins)
    for l in m.node_tree.links: print('P49 link',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
r=m.node_tree.nodes['ah_ramp'].color_ramp
print('P49 ramp',r.interpolation,[(round(e.position,2),tuple(round(c,3) for c in e.color)) for e in r.elements])

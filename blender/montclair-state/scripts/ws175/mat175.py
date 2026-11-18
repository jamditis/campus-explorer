import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.materials=['COLE_lawn_post2020_bs']
m=b.materials[0]
for n in m.node_tree.nodes:
    ins=[(i.name, round(i.default_value,3) if isinstance(i.default_value,float) else (tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked]
    extra={k:getattr(n,k) for k in ('wave_type','bands_direction','wave_profile','noise_dimensions','image','blend_type','operation') if hasattr(n,k)}
    print('N',n.bl_idname,n.name,n.label,extra,ins[:8])
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

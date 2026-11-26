import bpy, os
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b): b.materials=['Ground_ortho_grass']
m=b.materials[0]
for n in m.node_tree.nodes:
    ins=[(i.name, [ (l.from_node.name,l.from_socket.name) for l in i.links]) for i in n.inputs if i.is_linked]
    extra=getattr(n,'blend_type','') or getattr(n,'attribute_name','') or (n.image.name if getattr(n,'image',None) else '') or getattr(n,'uv_map','')
    print('M247',n.name,n.type,extra,ins,flush=True)
os._exit(0)

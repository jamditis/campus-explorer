import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (s,d): d.node_groups=['WS163_skirt_under_normalave_W']
ng=d.node_groups[0]
for n in ng.nodes:
    ins=[(i.name,getattr(i,'default_value',None) if not i.is_linked else 'L') for i in n.inputs if i.enabled]
    print('N',n.name,n.bl_idname,getattr(n,'operation',''),getattr(n,'domain',''),getattr(n,'data_type',''),[(a,(round(b,3) if isinstance(b,float) else (b.name if hasattr(b,'name') else (tuple(b) if hasattr(b,'__len__') and not isinstance(b,str) else b)))) for a,b in ins])
for l in ng.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

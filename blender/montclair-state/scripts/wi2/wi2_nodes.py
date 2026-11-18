import bpy
from mathutils import Vector
O=bpy.data.objects
g=O['QS_Richardson_lawn_grass_points_UNVERIFIED']
print('VIS',g.hide_render,g.hide_viewport,g.visible_get() if hasattr(g,'visible_get') else '', [c.name for c in g.users_collection], [ (c.name,c.hide_render) for c in g.users_collection])
md=g.modifiers['cx_grass']; print('MOD',md.show_render,md.show_viewport)
ng=md.node_group
for n in ng.nodes:
    ins=[(i.name, (i.default_value if hasattr(i,'default_value') and not hasattr(i.default_value,'__len__') else (tuple(i.default_value) if hasattr(i,'default_value') else None)), i.is_linked) for i in n.inputs]
    print('N',n.name,getattr(n,'data_type',''),ins)
for l in ng.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
for k,v in md.items(): print('IN',k, v if not hasattr(v,'name') else v.name)
m=g.matrix_world; n=len(g.data.vertices)
for i in (0,n-1100,n-1,n-500): print('V',i,tuple(round(x,2) for x in m@g.data.vertices[i].co))
# other objects named tuft
print('TUFT',[o.name for o in O if 'tuft' in o.name.lower()][:20])

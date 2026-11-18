import bpy, bmesh, math
CC='Center for Computing and Information Science roof (LiDAR)'
r=bpy.data.objects[CC]; print('MODS',[(m.name,m.node_group.name if m.node_group else None) for m in r.modifiers], 'mats',[m.name for m in r.data.materials], 'mw', r.matrix_world.translation[:])
me=r.data; print('V',len(me.vertices),'F',len(me.polygons),[ (a.name,a.domain,a.data_type) for a in me.attributes])
zs=[ (r.matrix_world@v.co).z for v in me.vertices]; print('z',min(zs),max(zs))
import collections
h=collections.Counter(round(z) for z in zs); print(sorted(h.items()))
xs=[(r.matrix_world@v.co).x for v in me.vertices]; ys=[(r.matrix_world@v.co).y for v in me.vertices]; print('bb',min(xs),max(xs),min(ys),max(ys))
# edge length stats
L=[ (me.vertices[e.vertices[0]].co-me.vertices[e.vertices[1]].co).length for e in me.edges]; L.sort(); print('edgeL med',L[len(L)//2],'p90',L[int(.9*len(L))])
m=r.data.materials[0]; 
for n in m.node_tree.nodes: 
    extra=''
    if n.type=='MATH': extra=n.operation+' '+str([round(i.default_value,3) for i in n.inputs if hasattr(i,'default_value') and not i.is_linked])
    if n.type=='ATTRIBUTE': extra=n.attribute_name
    print('N',n.name,n.type,extra)
for l in m.node_tree.links: print('L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
w=[o for o in bpy.data.objects if 'Computing' in o.name]; print('CCIS objs',[(o.name,o.type) for o in w])

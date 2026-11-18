import bpy, numpy as np
g=bpy.data.objects['QS_Richardson_lawn_grass_points_UNVERIFIED']
m=g.modifiers['cx_grass']; ng=m.node_group
for k in m.keys(): print('KEY',k,m[k])
for n in ng.nodes:
    ins=[(i.name, (tuple(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value)) for i in n.inputs if (not i.is_linked) and hasattr(i,'default_value')]
    print('NODE',n.bl_idname,n.name,getattr(n,'data_type',''),ins[:8])
for l in ng.links: print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
print('ATTRS',[a.name for a in g.data.attributes])
co=np.array([g.matrix_world@v.co for v in g.data.vertices])
for (x0,x1,y0,y1) in [(130,137,284,292),(130,137,276,284),(138,146,284,292)]:
    s=(co[:,0]>x0)&(co[:,0]<x1)&(co[:,1]>y0)&(co[:,1]<y1)
    print('DENS',x0,x1,y0,y1, round(s.sum()/((x1-x0)*(y1-y0)),1))
for c in bpy.data.collections:
    if 'grass' in c.name.lower(): print('COLL',c.name,[ (o.name,len(o.data.polygons) if o.type=='MESH' else 0, tuple(round(d,2) for d in o.dimensions)) for o in c.objects])

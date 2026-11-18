import bpy, numpy as np
r=bpy.data.objects['Calcia Hall roof (LiDAR)']; me=r.data; a=me.attributes['roofc']
print('ROOFC',a.domain,a.data_type)
c=np.array([tuple(d.color) for d in a.data])
print(' n',len(c),'alpha>=0.5 frac',round((c[:,3]>=0.5).mean(),3),'redish frac (r>g+0.08)',round((c[:,0]>c[:,1]+0.08).mean(),3),'mean',c.mean(0).round(3))
# per-face: faces where red (tile) would be chosen per alpha
m=bpy.data.materials['Roof_tile_or_membrane']; nt=m.node_tree
for nn in ('Math.003','OH_gate03','EI_flatmask','EM_gate37','Mix.002','Mix.006','Mix.007','RGB to BW'):
    n=nt.nodes.get(nn)
    if n: print(' NODE',nn,n.type,getattr(n,'operation',''),[(i.name,round(i.default_value,3) if isinstance(i.default_value,float) else '', [(l.from_node.name) for l in i.links]) for i in n.inputs if hasattr(i,'default_value')][:4],[(l.to_node.name,l.to_socket.name) for o in n.outputs for l in o.links][:3])
# compare: same counts for Dickson (white flat expected)
for nm in ('Dickson Hall roof (LiDAR)','Feliciano School of Business roof (LiDAR)'):
    o=bpy.data.objects.get(nm)
    if o and 'roofc' in o.data.attributes:
        cc=np.array([tuple(d.color) for d in o.data.attributes['roofc'].data]); print(' CMP',nm,'alpha>=0.5',round((cc[:,3]>=0.5).mean(),3),'red',round((cc[:,0]>cc[:,1]+0.08).mean(),3))

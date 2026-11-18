import bpy, numpy as np
r=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; me=r.data
print('mods',[(m.name,m.type) for m in r.modifiers],'mats',[m.name for m in me.materials],'users',[m.users for m in me.materials], 'meshusers',me.users)
print('keys',{k:r[k] for k in r.keys()})
print('attrs',[(a.name,a.domain,a.data_type) for a in me.attributes])
m=me.materials[0]
for n in m.node_tree.nodes:
    ins=[(i.name,[ (l.from_node.name,l.from_socket.name) for l in i.links]) for i in n.inputs if i.links]
    print(' N',n.name,n.type,getattr(n,'attribute_name',''),getattr(n,'blend_type',''),ins)
# which other objects use this material
print('others',[o.name for o in bpy.data.objects if o.type=='MESH' and o.data and m.name in [x.name for x in o.data.materials if x]][:20])
import mathutils
c=np.array([tuple(d.color) for d in me.attributes['roofc'].data]); print('roofc dom',me.attributes['roofc'].domain, 'rgb mean',c[:,:3].mean(0).round(3),'alpha hist',np.histogram(c[:,3],bins=5,range=(0,1))[0])
bb=[r.matrix_world@mathutils.Vector(b) for b in r.bound_box]; print('bbox',min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb))

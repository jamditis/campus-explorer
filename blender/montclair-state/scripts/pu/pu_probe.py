import bpy
from mathutils import Vector
w=bpy.data.objects['Dickson Hall walls']; me=w.data
print('SLOTS',[(s.link,s.material.name if s.material else None) for s in w.material_slots])
print('PROPS',{k:w[k] for k in w.keys() if not k.startswith('_')})
print('ATTRS',[(a.name,a.domain) for a in me.attributes])
m=w.material_slots[0].material
for n in sorted(m.node_tree.nodes,key=lambda n:n.name):
    if n.type=='MATH':
        ins=[]
        for i in n.inputs[:2]:
            ins.append(('L:'+i.links[0].from_node.name) if i.is_linked else round(i.default_value,4))
        print('N',n.name,n.operation,ins)
    elif n.type=='ATTRIBUTE': print('A',n.name,n.attribute_name,n.attribute_type)
mw=w.matrix_world; uv=me.uv_layers['facade'].data
import collections
for p in me.polygons:
    n=mw.to_3x3()@p.normal
    if abs(n.z)>0.1 or p.area<1: continue
    U=[uv[l].uv for l in p.loop_indices]
    print('F',p.index,'n%.2f,%.2f'%(n.x,n.y),'c',tuple(round(x,1) for x in mw@p.center),'a%.0f'%p.area,'u%.1f..%.1f v%.1f..%.1f'%(min(q.x for q in U),max(q.x for q in U),min(q.y for q in U),max(q.y for q in U)))
bb=[mw@Vector(c) for c in w.bound_box]; print('BB',min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb))
for o in bpy.data.objects:
    if 'ickson' in o.name and o.type=='MESH' and 'Window' not in o.name: 
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('O',o.name[:50],round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),round(min(v.z for v in bb),1),round(max(v.z for v in bb),1))

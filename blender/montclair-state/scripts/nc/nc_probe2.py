import bpy
from mathutils import Vector
O=bpy.data.objects
sp=O['CCOM newsroom grid spots (mx, GN instances)']
m=sp.modifiers[0]
for k,v in m.items(): print('MODIN',k,v)
for nd in m.node_group.nodes:
    if nd.type=='OBJECT_INFO': print('PROTO', nd.inputs[0].default_value)
for k in sp.data.attributes: print('ATTR',k.name)
for o in O:
    if 'proto' in o.name.lower() and ('spot' in o.name.lower() or 'mx' in o.name.lower()):
        print('P',o.name,[round(x,3) for x in o.dimensions], [tuple(round(c,3) for c in b) for b in (o.bound_box[0],o.bound_box[6])])
g=O['CCOM newsroom south glass (mx)'].material_slots[0].material
for nd in g.node_tree.nodes:
    print('GN',nd.type,nd.name,[(i.name,round(i.default_value,3) if isinstance(i.default_value,float) else None) for i in nd.inputs if hasattr(i,'default_value') and not i.is_linked][:30] if nd.type=='BSDF_PRINCIPLED' else '')
print('blend',g.blend_method if hasattr(g,'blend_method') else '', 'users',g.users)
c=O['CCOM newsroom pedestal + tripod cameras (mz, finer)']
pts=[c.matrix_world@v.co for v in c.data.vertices if (c.matrix_world@v.co).z<137.52]
cl=[]
for p in pts:
    for q in cl:
        if (q[0]-p).xy.length<0.6: q[1].append(p); break
    else: cl.append([p.copy(),[p]])
for q in cl:
    s=sum(q[1],Vector())/len(q[1]); print('BASE',round(s.x,2),round(s.y,2),len(q[1]))
d=O['CCOM newsroom anchor desk (mw)']; print('DESK',[tuple(round(x,2) for x in d.matrix_world@Vector(b)) for b in (d.bound_box[0],d.bound_box[6])])

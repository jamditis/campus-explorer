import bpy
from collections import Counter
c=Counter()
ex={}
for o in bpy.data.objects:
    if o.instance_type=='COLLECTION' and o.instance_collection:
        k=o.instance_collection.name; c[k]+=1; ex.setdefault(k,(o.name,tuple(round(s,2) for s in o.scale),o.instance_collection.library.filepath if o.instance_collection.library else 'local'))
for k,v in c.most_common(40): print('I',k,v,ex[k])
t=next(o for o in bpy.data.objects if o.name.startswith('WS120_Chapin_W_round_planter_ornamental_tree'))
import mathutils
vs=[t.matrix_world@v.co for v in t.data.vertices]
print('T bbox',[round(min(v[i] for v in vs),2) for i in range(3)],[round(max(v[i] for v in vs),2) for i in range(3)], [m.name for m in t.data.materials])
m=next(o for o in bpy.data.objects if o.name.startswith('WS120_Chapin_W_round_planter_mulch'))
vs=[m.matrix_world@v.co for v in m.data.vertices]
print('M bbox',[round(min(v[i] for v in vs),2) for i in range(3)],[round(max(v[i] for v in vs),2) for i in range(3)])

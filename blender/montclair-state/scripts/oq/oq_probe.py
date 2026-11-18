import bpy
from collections import Counter
c=bpy.data.collections['OO_context_wall_skirts_to_LiDAR_20261031oo']
for o in c.objects:
    me=o.data; hs=[]
    for p in me.polygons:
        zs=[me.vertices[i].co.z for i in p.vertices]; hs.append(max(zs)-min(zs))
    big=[h for h in hs if h>2.6]
    print('SK',o.name,len(hs),'h>2.6:',len(big),'maxh',round(max(hs),2),[m.name for m in me.materials])
for n in ['Center for Computing and Information Science walls','Calcia Hall walls','Memorial Auditorium walls']:
    o=bpy.data.objects[n]; print('W',n,[s.material.name if s.material else None for s in o.material_slots])
fp=bpy.data.objects['Footpaths_OSM']; print('FP mats',[s.material.name for s in fp.material_slots], [m.name for m in fp.modifiers])
for s in fp.material_slots:
    m=s.material
    for nd in m.node_tree.nodes: print('  node',nd.type,nd.name, [ (i.name, i.default_value[:] if hasattr(i.default_value,'__len__') else i.default_value) for i in nd.inputs if i.name in('Base Color','Roughness','Color','Fac','Value') and not i.is_linked][:3])
# windows on context buildings? look for objects with names containing building names
cnt=Counter()
for o in bpy.data.objects:
    for k in ['Computing','Environmental','Speech','Calcia','Memorial']:
        if k in o.name: cnt[k]+=1; print('OBJ',o.name,o.type) if cnt[k]<6 else None

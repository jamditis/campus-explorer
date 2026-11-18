import bpy
o=bpy.data.objects['Schmitt Hall roof (LiDAR)']; me=o.data
print('MATS',[m.name if m else None for m in me.materials], 'lib',me.library)
for a in me.attributes: print('ATTR',a.name,a.domain,a.data_type)
from collections import Counter
for a in me.attributes:
    if a.domain=='FACE' and a.data_type in('INT','FLOAT','INT8','BOOLEAN'):
        print(a.name,Counter(round(d.value,2) if isinstance(d.value,float) else d.value for d in a.data).most_common(8))
print(Counter(p.material_index for p in me.polygons))
m=bpy.data.materials['Roof_tile_or_membrane']
for n in m.node_tree.nodes:
    extra=''
    if n.type=='ATTRIBUTE': extra=n.attribute_name
    print('NODE',n.name,n.type,extra,[ (i.name,i.default_value if hasattr(i,'default_value') and not hasattr(i.default_value,'__len__') else '') for i in n.inputs if not i.is_linked][:4])
for l in m.node_tree.links: print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
print('users',m.users)
w=bpy.data.objects.get('Schmitt Hall walls'); print('walls mats',[s.material.name if s.material else None for s in w.material_slots])
ws=[ob for ob in bpy.data.objects if ob.name.startswith('SCH_win_')]
print('nwin',len(ws), ws[0].data.name, ws[0].data.library, [s.material.name for s in ws[0].material_slots if s.material], [s.link for s in ws[0].material_slots])

import bpy
o=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; me=o.data
for xc in (-235,-215,-205):
    fs=[]
    for p in me.polygons:
        c=p.center
        if abs(c.x-xc)<0.3: ys=[me.vertices[i].co.y for i in p.vertices]; fs.append((round(min(ys),2),round(max(ys),2),p.material_index))
    print('P3 faces',xc,sorted(fs))
from collections import Counter
print('P3 matidx',Counter(p.material_index for p in me.polygons))
for mn in ('WS27_curb_concrete_UNVERIFIED','WS27_gutter_pan_concrete_UNVERIFIED','WS27_CollegeAve_asphalt_2020ortho','Kasser_apron_concrete_cm'):
    m=bpy.data.materials.get(mn)
    if not m: print('P3 nomat',mn); continue
    print('P3 mat',mn,[(n.type,n.name,(n.image.name if getattr(n,'image',None) else ''),[ (i.name,tuple(round(x,3) for x in i.default_value) if hasattr(i.default_value,'__len__') else round(i.default_value,3)) for i in n.inputs if not i.is_linked and i.name in ('Base Color','Roughness','Fac','Color1','Color2','Scale','A','B')]) for n in m.node_tree.nodes])
    print('P3 links',mn,[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])

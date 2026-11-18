import bpy
for n in ('NG cafe chair 0_0 seat','NG cafe chair 0_0 back','NG cafe table 0 top','NK S office chair 00 seat','NG chevron bench seat'):
    o=bpy.data.objects[n]; print('P2',n,[(s.link,s.material.name if s.material else None) for s in o.material_slots],tuple(round(c,3) for c in o.color), o.data.materials[:] and o.data.materials[0].name)
    m=o.active_material; nt=m.node_tree
    print('P2 nodes',[nd.type for nd in nt.nodes], [tuple(round(x,3) for x in nt.nodes['Principled BSDF'].inputs['Base Color'].default_value)] if 'Principled BSDF' in nt.nodes else '')

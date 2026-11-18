import bpy
O=bpy.data.objects
for n in ['WV_stone_west_LiDAR_patch_UNVERIFIED']:
    o=O[n]; me=o.data; print('WV',len(me.vertices),len(me.polygons),[a.name for a in me.attributes], o.matrix_world.translation)
for o in O:
    if o.type=='MESH' and ('546643369' in o.name or '546643370' in o.name): 
        bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
        print('OBJ',o.name,len(o.data.polygons),round(min(b.x for b in bb),1),round(max(b.x for b in bb),1),round(min(b.y for b in bb),1),round(max(b.y for b in bb),1))
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']
nt=m.node_tree; b=nt.nodes['Principled BSDF']
for s in ('Base Color','Roughness','Normal'):
    for l in b.inputs[s].links: print('IN',s,l.from_node.name,l.from_socket.name)
for l in nt.links:
    if l.to_node.name in ('TS_final',): print('TSF',l.from_node.name,l.from_socket.name,'->',l.to_socket.identifier)
print('users',[o.name for o in O if o.type=='MESH' and any(s.material==m for s in o.material_slots)])

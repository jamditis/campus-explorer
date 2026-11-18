import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('M39 mods',[m.type+':'+m.name for m in T.modifiers])
for s in T.material_slots:
    m=s.material; print('M39 mat',m.name)
    for n in m.node_tree.nodes:
        extra=''
        if n.type=='TEX_IMAGE' and n.image: extra=n.image.name+' '+str(tuple(n.image.size))
        print('M39   ',n.type,n.name,n.label,extra)
    for l in m.node_tree.links: print('M39   L',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)

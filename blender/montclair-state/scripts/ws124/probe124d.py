import bpy
o=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_frame_canopy'))
mw=o.matrix_world
print('MATS',[m.name if m else None for m in o.data.materials])
for p in o.data.polygons:
    c=mw@p.center
    if c.z>127.8: 
        vs=[mw@o.data.vertices[i].co for i in p.vertices]
        print('P',p.material_index,round(c.x,2),round(c.y,2),round(c.z,2),[round(v,2) for v in p.normal],'x',round(min(v.x for v in vs),2),round(max(v.x for v in vs),2),'y',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2))
d=next(o for o in bpy.data.objects if o.name.startswith('WS123_Chapin_W_entrance_storefront'))
print('DMATS',[m.name for m in d.data.materials])
g=d.data.materials[1]; print('GLASS nodes',[(n.type,n.name) for n in g.node_tree.nodes])

import bpy
for o in bpy.data.objects:
    if 'tk_obj' in o and o.type=='MESH':
        me=o.data; bad=[p for p in me.polygons if p.normal.z<-0.1 and p.center.z>o.data.vertices[0].co.z+1]
        nm=sum(1 for e in me.edges if len([1 for p in me.polygons if e.key in p.edge_keys])!=2) if len(me.edges)<400 else -1
        print('TKP',o.name,len(me.polygons),'slanted',len(bad),[ (round(p.center.x,1),round(p.center.y,1),round(p.center.z,1),round(p.normal.z,2)) for p in bad[:5]],'nonmanifold',nm)

import bpy
for n in ('Feliciano School of Business roof (LiDAR)','Feliciano School of Business walls'):
    o=bpy.data.objects[n]; m=o.data; mw=o.matrix_world; R=mw.to_3x3()
    print('OBJ',n,len(m.vertices),len(m.polygons),[s.material.name if s.material else None for s in o.material_slots],[ (md.name,md.type) for md in o.modifiers], o.data.users, o.data.library)
    import collections
    c=collections.Counter(); zs=[]
    for p in m.polygons:
        nz=abs((R@p.normal).normalized().z); k='flat' if nz>=0.95 else ('slope' if nz>0.15 else 'vert')
        c[(k,p.material_index)]+=1
    print(' faces',dict(c))
    vz=[(mw@v.co).z for v in m.vertices]; print(' z',min(vz),max(vz))
    bb=[mw@v.co for v in m.vertices]; print(' x',min(v.x for v in bb),max(v.x for v in bb),'y',min(v.y for v in bb),max(v.y for v in bb))

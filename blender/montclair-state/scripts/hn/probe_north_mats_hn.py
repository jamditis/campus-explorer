import bpy, collections
for gn in ('North_terrain_LiDAR_1m','North_skirt_lowdetail_4m'):
    g=bpy.data.objects[gn]; M=g.matrix_world; c=collections.Counter()
    for p in g.data.polygons:
        w=M@p.center
        if -215<w.x<-130 and -30<w.y<55: c[p.material_index]+=1
    print('NM',gn,[(i,g.material_slots[i].material.name if g.material_slots[i].material else None,n) for i,n in c.most_common()])
    print('NM slots',gn,[s.material.name if s.material else None for s in g.material_slots])
print('NM lawnmats',[m.name for m in bpy.data.materials if 'awn' in m.name or 'COLE_lawn' in m.name])

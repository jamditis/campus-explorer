import bpy, collections
o=bpy.data.objects['UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED']
mw=o.matrix_world; me=o.data
d=collections.defaultdict(list)
for p in me.polygons:
    c=mw@p.center; d[p.material_index].append(c)
for k,v in d.items():
    xs=[c.x for c in v]; ys=[c.y for c in v]; zs=[c.z for c in v]
    print('CUR',k,me.materials[k].name if k<len(me.materials) else None,len(v),round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2))
w=bpy.data.objects['Freeman Hall walls']; print('WALL',w.type,len(w.data.polygons),[m.name for m in w.modifiers],w.data.users)
mw=w.matrix_world
for p in w.data.polygons:
    c=mw@p.center
    if -92<c.x<-83 and c.y>-173 and c.z<140:
        vs=[mw@w.data.vertices[i].co for i in p.vertices]
        print('WF',p.index,[tuple(round(a,2) for a in v) for v in vs], tuple(round(a,2) for a in (mw.to_3x3()@p.normal)))
for n in ['UV_Freeman_N_entrance_steps_handrails_UNVERIFIED','VC_Freeman_N_entrance_glass_backplanes_UNVERIFIED']:
    ob=bpy.data.objects[n]
    print(n, ob.parent.name if ob.parent else None, ob.users_collection[0].name)
print('TERR', [ (n) for n in ['Terrain','DTM'] if bpy.data.objects.get(n)])

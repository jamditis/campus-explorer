import bpy
f=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_frame_canopy'))
for p in f.data.polygons:
    vs=[f.matrix_world@f.data.vertices[i].co for i in p.vertices]
    if max(v.z for v in vs)<=127.73 and min(v.x for v in vs)>-209.3:
        print('F',p.index,[round(min(v[i] for v in vs),2) for i in range(3)],[round(max(v[i] for v in vs),2) for i in range(3)],tuple(round(c,2) for c in p.normal))
for nm in ('Footpaths_OSM','OZ_walk_joints','PA_walk_panel','Roads_OSM','WS102_CollegeAve_S_carriageway'):
    o=next(o for o in bpy.data.objects if o.name.startswith(nm)); n=0; zs=[]
    for p in o.data.polygons:
        c=o.matrix_world@p.center
        if -213.0<c.x<-209.0 and -201.5<c.y<-196.0: n+=1; zs.append(round(c.z,2))
    print('S',nm,n,sorted(zs)[:5],sorted(zs)[-5:],[m.type for m in o.modifiers])

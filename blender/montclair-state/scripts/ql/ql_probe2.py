import bpy, numpy as np
for n in ['Center for Computing and Information Science walls','QF_CCIS_stucco_skin_recessed_openings_photo']:
    o=bpy.data.objects[n]; dg=bpy.context.evaluated_depsgraph_get(); me=o.evaluated_get(dg).data; M=o.matrix_world
    print('OBJ',n,len(me.polygons),[m.name for m in o.modifiers])
    rows=[]
    for p in me.polygons:
        nr=(M.to_3x3()@p.normal).normalized()
        if nr.x<0.5 or abs(nr.z)>0.3: continue
        c=M@p.center
        if c.y<195: continue
        vs=np.array([M@me.vertices[i].co for i in p.vertices])
        rows.append((round(nr.x,2),round(nr.y,2),round(c.x,1),round(c.y,1),round(vs[:,2].min(),1),round(vs[:,2].max(),1),round(p.area,1), vs[:,0].min().round(1),vs[:,0].max().round(1),vs[:,1].min().round(1),vs[:,1].max().round(1)))
    rows.sort(key=lambda r:-r[6])
    for r in rows[:25]: print(' ',r)

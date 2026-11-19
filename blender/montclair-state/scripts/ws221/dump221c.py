import bpy,bmesh
for nm in ('WS67_CollegeAve_gap_asphalt','WS27_CollegeAve_carriageway_2020ortho'):
    ob=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; M=ob.matrix_world
    bm=bmesh.new(); bm.from_mesh(ob.data)
    print('P221 OBJ',ob.name,len(bm.verts),[m.type for m in ob.modifiers])
    for v in bm.verts:
        w=M@v.co
        if -249.9<=w.x<=-248.8 and -58.6<=w.y<=-55.9: print('P221 %s %d %.3f %.3f %.3f %s %d'%(nm[:4],v.index,*w,'B' if v.is_boundary else '-',len(v.link_faces)))

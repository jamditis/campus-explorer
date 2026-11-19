import bpy
for nm,box in (('WS220_CollegeAve_curb_jog_return_UNVERIFIED',(-249.0,-248.3,-54.0,-52.7)),('WS27_CollegeAve_curb_left_UNVERIFIED',(-248.6,-247.8,-53.2,-52.0)),('WS27_CollegeAve_carriageway',(-249.2,-248.2,-54.6,-52.6))):
    o=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; M=o.matrix_world
    print('P222 ==',o.name,len(o.data.vertices),[m.name for m in o.modifiers],[s.material.name for s in o.material_slots if s.material][:3])
    for i,v in enumerate(o.data.vertices):
        w=M@v.co
        if box[0]<=w.x<=box[1] and box[2]<=w.y<=box[3]: print('P222  v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
o=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; n=len(o.data.vertices)
print('P222 return first ring',[tuple(round(c,3) for c in o.matrix_world@o.data.vertices[i].co) for i in range(5)])
print('P222 return last ring',[tuple(round(c,3) for c in o.matrix_world@o.data.vertices[i].co) for i in range(n-5,n)])

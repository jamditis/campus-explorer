import bpy, os, bmesh
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
for pfx in ['WS70_gap_strip_grass_berms','WS69_CollegeAve_gap_strip_curbs','ey_rhd_se_crosswalks']:
    o=[x for x in bpy.data.objects if x.name.startswith(pfx)][0]; mw=o.matrix_world
    print('OBJ',o.name,len(o.data.vertices),len(o.data.polygons),[m.type for m in o.modifiers],flush=True)
    bm=bmesh.new(); bm.from_mesh(o.data)
    if pfx.startswith('WS70'):
        for e in bm.edges:
            if e.is_boundary:
                for v in e.verts:
                    p=mw@v.co
                    if -258<p.x<-248 and -63<p.y<-55: print('B70',v.index,round(p.x,3),round(p.y,3),round(p.z,3))
    if pfx.startswith('ey'):
        for f in bm.faces:
            ps=[mw@v.co for v in f.verts]; xs=[p.x for p in ps]; ys=[p.y for p in ps]
            if -262<min(xs) and max(xs)<-256 and min(ys)<-55: print('FEY',f.index,round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(ps[0].z,3))
    if pfx.startswith('WS69'):
        xs=[(mw@v.co) for v in o.data.vertices]; sel=[p for p in xs if -258<p.x<-248 and -63<p.y<-55]
        print('V69',len(sel),[ (round(p.x,2),round(p.y,2),round(p.z,2)) for p in sel[:40]])

import bpy, bmesh
for nm in ['WS163_Lot3_aisle_S_drive_to_NormalAve_OSM232846667_LiDAR2023_UN','WS162_Lot3_S_end_apron_feather_UNVERIFIED']:
    o=[x for x in bpy.data.objects if x.name.startswith(nm)][0]
    bm=bmesh.new(); bm.from_mesh(o.data); M=o.matrix_world
    print('OBJ',o.name,'v',len(bm.verts),'f',len(bm.faces),'solidify?',[m.type for m in o.modifiers], 'loc',tuple(o.location))
    be=[e for e in bm.edges if e.is_boundary]
    print('NBOUND',len(be))
    # walk loops
    seen=set(); 
    for e0 in be:
        if e0.index in seen: continue
        loop=[e0.verts[0]]; cur=e0.verts[1]; prev=e0; seen.add(e0.index)
        while cur!=loop[0]:
            loop.append(cur)
            nx=[e for e in cur.link_edges if e.is_boundary and e.index not in seen]
            if not nx: break
            prev=nx[0]; seen.add(prev.index); cur=prev.other_vert(cur)
        print('LOOP',len(loop),' '.join(f'{(M@v.co).x:.2f},{(M@v.co).y:.2f},{(M@v.co).z:.2f}' for v in loop))

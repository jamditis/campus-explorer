# pt (Nov 1 2026): pre-existing dark band under the Calcia roof edge. Diagnosis (rays + edge survey): the LiDAR wall shell stops at
# 144.1-147.3 m along many top edges while the flat roof sits at 147.37 m, leaving an open 0.1-3.2 m strip through which the dark
# hollow interior shows. Fix: PT_Calcia_wall_top_infill_UNVERIFIED, one vertical quad per top boundary edge (taken from the uncut
# PS_backup_Calcia_walls) from the wall top up to 147.42 m, same wall material, facade UV continued in metres (brick courses line up),
# no win_top attribute (so the slot shader draws no windows on it). Additive; REVERT=1 deletes it. Wall heights UNVERIFIED.
import bpy, bmesh, os
REV=os.environ.get('REVERT')=='1'; ON='PT_Calcia_wall_top_infill_UNVERIFIED'; ZT=147.42
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_PT_TOPFILL')
if not REV:
    w=bpy.data.objects['Calcia Hall walls']; mw=w.matrix_world; imw=mw.inverted(); src=bpy.data.meshes['PS_backup_Calcia_walls']
    bm=bmesh.new(); bm.from_mesh(src); uvs=bm.loops.layers.uv['facade']
    out=bmesh.new(); ouv=out.loops.layers.uv.new('facade'); n=0; dzmax=0
    for e in bm.edges:
        if not e.is_boundary: continue
        a=mw@e.verts[0].co; b=mw@e.verts[1].co
        if min(a.z,b.z)<139 or abs(a.z-b.z)>0.4 or max(a.z,b.z)>ZT-0.05: continue
        f=e.link_faces[0]
        if (mw@f.calc_center_median()).z>min(a.z,b.z): continue
        lp={l.vert:l for l in f.loops}; ua=lp[e.verts[0]][uvs].uv.copy(); ub=lp[e.verts[1]][uvs].uv.copy()
        A=imw@a; B=imw@b; At=A.copy(); Bt=B.copy(); At.z+= (ZT-a.z)/mw.to_scale().z; Bt.z+=(ZT-b.z)/mw.to_scale().z
        vs=[out.verts.new(p) for p in (B,A,At,Bt)]
        nf=out.faces.new(vs); nf.material_index=f.material_index
        for l,uv in zip(nf.loops,(ub,ua,(ua.x,ua.y+ZT-a.z),(ub.x,ub.y+ZT-b.z))): l[ouv].uv=uv
        # keep the face normal on the same side as the wall face
        if nf.normal.dot(f.normal)<0: nf.normal_flip()
        n+=1; dzmax=max(dzmax,ZT-min(a.z,b.z))
    m2=bpy.data.meshes.new(ON); out.to_mesh(m2); out.free(); bm.free()
    for m in w.data.materials: m2.materials.append(m)
    o=bpy.data.objects.new(ON,m2); o.matrix_world=mw.copy(); w.users_collection[0].objects.link(o)
    for k in w.keys():
        try: o[k]=w[k]
        except Exception: pass
    o['win_top']=0.0; o['win_h']=0.0   # object attrs drive the facade shader (brick etc.); no windows on the infill
    for i,sl in enumerate(w.material_slots):   # Calcia's brick is linked at OBJECT level over the mesh's stucco slot
        if i<len(o.material_slots): o.material_slots[i].link=sl.link; o.material_slots[i].material=sl.material
    print('PT_TOPFILL slots',[(sl.link,sl.material.name if sl.material else None) for sl in o.material_slots])
    print('PT_TOPFILL props',list(o.keys()))
    print('PT_TOPFILL quads',n,'max dz',round(dzmax,2))

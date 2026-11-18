# pt (Nov 1 2026): Feliciano 156.6 tier end seam. The old LiDAR wall faces lying in the plane of PN_Feliciano_tier_156.6 face 55
# (north face) have inward (flipped) normals and shade differently from the tier wall standing 3-6 cm in front -> visible end edge.
# Fix: those coplanar old-wall faces (within 0.15 m of the tier plane, along its span +-8 m, normals opposite) are flipped to face
# outward like the tier wall. Original mesh kept as fake-user 'PT_backup_Feliciano_walls'; REVERT=1 restores it exactly. UNVERIFIED.
import bpy, bmesh, os
REV=os.environ.get('REVERT')=='1'; BK='PT_backup_Feliciano_walls'
w=bpy.data.objects['Feliciano School of Business walls']; me=w.data; mw=w.matrix_world
if BK in bpy.data.meshes:
    bk=bpy.data.meshes[BK]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(me); bm.free(); me.update(); bpy.data.meshes.remove(bk); print('REVERTED_PT_FELWALLS')
if not REV:
    bk=me.copy(); bk.name=BK; bk.use_fake_user=True
    t=[x for x in bpy.data.objects if x.name.startswith('PN_Feliciano_tier_156.6')][0]; tw=t.matrix_world; tp=t.data.polygons[55]
    tn=(tw.to_3x3()@tp.normal).normalized(); tc=tw@tp.center
    vs=[tw@t.data.vertices[i].co for i in tp.vertices]; ax=(vs[2]-vs[1]); ax.z=0; L=ax.length; ax.normalize()
    bm=bmesh.new(); bm.from_mesh(me); fl=[]
    for f in bm.faces:
        n=(mw.to_3x3()@f.normal).normalized(); c=mw@f.calc_center_median()
        if n.dot(tn)<-0.95 and abs((c-tc).dot(tn))<0.15 and abs((c-tc).dot(ax))<L/2+8: fl.append(f)
    bmesh.ops.reverse_faces(bm,faces=fl)
    # the old wall actually stands ~5 cm PROUD of the tier face here, so its sloped pq top edge shows as a slanted line:
    # push its verts above the tier bottom (z>139.9) within the tier span to 3 cm behind the tier plane
    imw=mw.inverted(); zb=min(v.z for v in vs)+0.1; npush=0
    for v in {v for f in fl for v in f.verts}:
        g=mw@v.co; d=(g-tc).dot(tn)
        if g.z>zb and abs((g-tc).dot(ax))<L/2-0.05 and d>-0.03:
            v.co=imw@(g-tn*(d+0.03)); npush+=1
    print('PT_FEL_PUSHED',npush)
    bm.to_mesh(me); bm.free(); me.update(); print('PT_FEL_FLIPPED',len(fl))

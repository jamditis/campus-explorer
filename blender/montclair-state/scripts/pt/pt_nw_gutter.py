# pt (Nov 1 2026): NW tower stray gutter. The 4.5 m PO box-gutter run for tier 153.3 at x -257.7..-253.3, y ~210.8, z 153.3
# is half-buried in the old LiDAR wall that stands ~2.3 m above that roof, so from the NW it reads as a dark bar sticking out
# of a blank wall (no roof edge to drain). The run (one closed 8-vert box, no downpipe) is removed. UNVERIFIED.
# Original mesh kept as fake-user 'PT_backup_PO_gutters'; REVERT=1 restores it exactly.
import bpy, bmesh, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; BK='PT_backup_PO_gutters'
o=bpy.data.objects['PO_Feliciano_gutters_downpipes_UNVERIFIED']; me=o.data; mw=o.matrix_world
if BK in bpy.data.meshes:
    bk=bpy.data.meshes[BK]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(me); bm.free(); me.update(); bpy.data.meshes.remove(bk); print('REVERTED_PT_GUTTER')
if not REV:
    bk=me.copy(); bk.name=BK; bk.use_fake_user=True
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    tgt=Vector((-255.5,210.82,153.31)); seed=min(bm.faces,key=lambda f:((mw@f.calc_center_median())-tgt).length)
    seen=set(); st=[seed]
    while st:
        f=st.pop()
        if f in seen: continue
        seen.add(f); st+= [g for e in f.edges for g in e.link_faces]
    vs={v for f in seen for v in f.verts}; c=sum((mw@v.co for v in vs),Vector())/len(vs)
    assert len(vs)==8 and (c-tgt).length<0.3, (len(vs),c)
    bmesh.ops.delete(bm,geom=list(vs),context='VERTS'); bm.to_mesh(me); bm.free(); me.update(); print('PT_NW_GUTTER_REMOVED V',len(me.vertices))
# --- matching PN eave segment (same tier 153.3 north edge, x > -257.3, y > 209.5): bisected at x=-257.3 and the part buried
#     in / standing proud of the old wall removed; the west-side eave run and its NW corner stay.
BK2='PT_backup_PN_eaves'; e=bpy.data.objects['PN_Feliciano_eaves_UNVERIFIED']; em=e.data; ew=e.matrix_world
if BK2 in bpy.data.meshes:
    bk=bpy.data.meshes[BK2]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(em); bm.free(); em.update(); bpy.data.meshes.remove(bk); print('REVERTED_PT_EAVE')
if not REV:
    bk=em.copy(); bk.name=BK2; bk.use_fake_user=True
    bm=bmesh.new(); bm.from_mesh(em); iw=ew.inverted()
    sel=[f for f in bm.faces if all((ew@v.co).y>209.5 and (ew@v.co).x>-259.5 and (ew@v.co).x<-252.5 and 152.9<(ew@v.co).z<153.6 for v in f.verts)]
    geom=sel+list({x for f in sel for x in f.edges})+list({v for f in sel for v in f.verts})
    bmesh.ops.bisect_plane(bm,geom=geom,dist=0.0005,plane_co=iw@Vector((-257.3,0,0)),plane_no=(iw.to_3x3()@Vector((1,0,0))).normalized())
    dl=[f for f in bm.faces if (lambda c:(c.x>-257.3 and c.x<-252.5 and c.y>209.5 and 152.9<c.z<153.6))(ew@f.calc_center_median())]
    bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(em); bm.free(); em.update(); print('PT_NW_EAVE_TRIM faces',len(dl),'V',len(em.vertices))

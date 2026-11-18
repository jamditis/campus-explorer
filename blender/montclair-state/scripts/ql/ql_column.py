# ql (5): the cover-wall window column at y ~207.7-209.3 had lost everything but its jambs (removed in ql 2). Rebuild it as a
# copy of the next column (islands of QF_qe_cover_wall_windows_kept_red with x>28.9, y within 210.6-212.4) shifted -3.0 m in y
# (the 3 m column rhythm), new object QL_ccis_cover_wall_window_column_UNVERIFIED. REVERT=1 removes it.
import bpy, os, bmesh
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; NM='QL_ccis_cover_wall_window_column_UNVERIFIED'
o=bpy.data.objects.get(NM)
if o: me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
if not REV:
    src=bpy.data.objects['QF_qe_cover_wall_windows_kept_red_UNVERIFIED']; M=src.matrix_world
    bm=bmesh.new(); bm.from_mesh(src.data); bm.faces.ensure_lookup_table(); seen=set(); keep=set()
    for f in bm.faces:
        if f.index in seen: continue
        st=[f]; comp=[]; seen.add(f.index)
        while st:
            g=st.pop(); comp.append(g)
            for e in g.edges:
                for g2 in e.link_faces:
                    if g2.index not in seen: seen.add(g2.index); st.append(g2)
        vs=[M@v.co for g in comp for v in g.verts]
        if min(v.x for v in vs)>28.9 and min(v.y for v in vs)>=210.6 and max(v.y for v in vs)<=212.4: keep.update(g.index for g in comp)
    dele=[f for f in bm.faces if f.index not in keep]; bmesh.ops.delete(bm,geom=dele,context='FACES')
    bm.transform(M); bmesh.ops.translate(bm,verts=bm.verts,vec=Vector((0,-3.0,0)))
    me=bpy.data.meshes.new(NM); bm.to_mesh(me); bm.free()
    for m in src.data.materials: me.materials.append(m)
    ob=bpy.data.objects.new(NM,me); (src.users_collection[0] if src.users_collection else bpy.context.scene.collection).objects.link(ob)
    ob['UNVERIFIED_ql']='copy of the next cover-wall window column shifted -3 m (rhythm), UNVERIFIED'
    print('COLUMN faces',len(me.polygons),'kept',len(keep))

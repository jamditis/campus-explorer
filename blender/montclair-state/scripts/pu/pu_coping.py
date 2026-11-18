# pu: stray generic Roof_coping run at z~146 crossing the face of Dickson's taller west/north walls (it belongs to the
# lower east roof level 145.3 but the LiDAR outline carried it along walls that continue up to ~150 m), printing as a
# dark diagonal line across the west facade. Islands of Roof_coping whose every vertex lies within 0.8 m of a Dickson wall
# face AND >= 0.5 m below that wall face's top are removed (mesh swap; original kept as fake-user PU_backup_Roof_coping).
# REVERT=1 swaps the original mesh back.
import bpy, bmesh, os
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; BK='PU_backup_Roof_coping'
o=bpy.data.objects['Roof_coping']
if BK in bpy.data.meshes:
    cur=o.data; b=bpy.data.meshes[BK]; nm=cur.name; o.data=b; b.use_fake_user=False
    bpy.data.meshes.remove(cur); b.name=nm; print('REVERTED_PU_COPING',len(b.vertices))
if not REV:
    w=bpy.data.objects['Dickson Hall walls']; wm=w.matrix_world
    bmw=bmesh.new(); bmw.from_mesh(w.data); bmw.transform(wm); bmw.faces.ensure_lookup_table()
    tops=[max(v.co.z for v in f.verts) for f in bmw.faces]
    bvh=BVHTree.FromBMesh(bmw)
    me=o.data; om=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    seen=set(); kill=[]; nis=0
    for v0 in bm.verts:
        if v0.index in seen: continue
        isl=[]; st=[v0]; seen.add(v0.index)
        while st:
            v=st.pop(); isl.append(v)
            for e in v.link_edges:
                u=e.other_vert(v)
                if u.index not in seen: seen.add(u.index); st.append(u)
        ok=True
        for v in isl:
            p=om@v.co; loc,nor,fi,dist=bvh.find_nearest(p)
            if fi is None or dist>0.8 or tops[fi]-p.z<0.5: ok=False; break
        if ok: kill+=isl; nis+=1
    print('PU_COPING islands',nis,'verts',len(kill))
    bk=me.copy(); bk.name=BK; bk.use_fake_user=True
    if kill: bmesh.ops.delete(bm,geom=kill,context='VERTS')
    bm.to_mesh(me); bm.free(); bmw.free(); me.update()
    print('PU_COPING now',len(me.vertices))

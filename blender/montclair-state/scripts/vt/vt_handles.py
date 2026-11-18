import bpy, bmesh
from mathutils import Vector as V
o=bpy.data.objects['UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED']; mw=o.matrix_world; mi=mw.inverted()
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
seen=set(); isl=[]
for f in bm.faces:
    if f in seen: continue
    st=[f]; grp=[]; seen.add(f)
    while st:
        g=st.pop(); grp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h not in seen: seen.add(h); st.append(h)
    vs={v for g in grp for v in g.verts}
    ws=[mw@v.co for v in vs]
    mn=V([min(w[i] for w in ws) for i in range(3)]); mx=V([max(w[i] for w in ws) for i in range(3)])
    isl.append((vs,mn,mx,grp[0].material_index))
moved=0
for vs,mn,mx,mat in isl:
    h=mx.z-mn.z; wxy=max(mx.x-mn.x,mx.y-mn.y)
    if h<1.0 and wxy<0.25 and 132.3<(mn.z+mx.z)/2<135.5:
        dz=131.45-(mn.z+mx.z)/2
        for v in vs:
            w=mw@v.co; w.z+=dz; v.co=mi@w
        moved+=1; print('HANDLE',[round(a,2) for a in mn],[round(a,2) for a in mx],mat,round(dz,2))
bm.to_mesh(o.data); bm.free(); o.data.update()
print('ISL',len(isl),'MOVED',moved)
if moved: bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')

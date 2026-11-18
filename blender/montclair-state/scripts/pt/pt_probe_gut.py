import bpy, bmesh
o=bpy.data.objects['PO_Feliciano_gutters_downpipes_UNVERIFIED']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
seen=set(); st=[bm.faces[76]]
while st:
    f=st.pop()
    if f.index in seen: continue
    seen.add(f.index)
    for e in f.edges:
        for g in e.link_faces: st.append(g)
vs={v for i in seen for v in bm.faces[i].verts}
P=[mw@v.co for v in vs]
print('ISL faces',len(seen),'verts',len(vs),'mat',{bm.faces[i].material_index for i in seen})
for a in range(3): print('AX',a,round(min(p[a] for p in P),3),round(max(p[a] for p in P),3))
for i in sorted(seen): f=bm.faces[i]; print('F',i,tuple(round(x,2) for x in (mw.to_3x3()@f.normal)),tuple(round(x,2) for x in mw@f.calc_center_median()),round(f.calc_area(),3))
# old wall faces 109-113
w=bpy.data.objects['Feliciano School of Business walls']; m=w.data; ww=w.matrix_world
for fi in range(107,116):
    p=m.polygons[fi]; print('W',fi,tuple(round(x,2) for x in ww.to_3x3()@p.normal),[tuple(round(x,2) for x in ww@m.vertices[i].co) for i in p.vertices])
for ob in bpy.data.objects:
    if ob.name.startswith('PN_Feliciano_tier'):
        P=[ob.matrix_world@v.co for v in ob.data.vertices]
        near=[p for p in P if abs(p.x+253.5)<4 and abs(p.y-210.9)<4]
        if near: print('TIERNEAR',ob.name,[tuple(round(x,2) for x in p) for p in near[:8]])

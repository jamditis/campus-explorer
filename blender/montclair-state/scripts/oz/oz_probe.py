import bpy, bmesh, math
F=bpy.data.objects['Footpaths_OSM']; print('MODS',[(m.name,m.type,m.show_render) for m in F.modifiers])
print('RAW',len(F.data.vertices),len(F.data.polygons),[a.name for a in F.data.attributes])
dg=bpy.context.evaluated_depsgraph_get(); me=F.evaluated_get(dg).to_mesh()
b=bmesh.new(); b.from_mesh(me); b.transform(F.matrix_world)
print('EVAL',len(b.verts),len(b.faces))
# islands
b.faces.ensure_lookup_table(); seen=set(); isl=[]
for f in b.faces:
    if f.index in seen: continue
    st=[f]; seen.add(f.index); n=0; area=0; xs=[];ys=[]
    while st:
        g=st.pop(); n+=1; area+=g.calc_area(); c=g.calc_center_median(); xs.append(c.x); ys.append(c.y)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); st.append(h)
    isl.append((round(area),n,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys))))
isl.sort(reverse=True); print('ISLANDS',len(isl)); print(isl[:25])
print('OTHER walk-like objs',[o.name for o in bpy.data.objects if 'walk' in o.name.lower()][:40])

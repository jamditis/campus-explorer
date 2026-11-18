import bpy, bmesh
from mathutils import Vector
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
bd=set(e for e in bm.edges if e.is_boundary)
seen=set(); loops=[]
for e in bd:
    if e in seen: continue
    comp=[]; st=[e]
    while st:
        x=st.pop()
        if x in seen: continue
        seen.add(x); comp.append(x)
        for v in x.verts:
            for y in v.link_edges:
                if y in bd and y not in seen: st.append(y)
    vs=set(v for x in comp for v in x.verts)
    P=[M@v.co for v in vs]
    mn=[round(min(p[i] for p in P),1) for i in range(3)]; mx=[round(max(p[i] for p in P),1) for i in range(3)]
    loops.append((len(comp),mn,mx))
loops.sort(key=lambda l:-l[0])
print('NLOOPS',len(loops))
for l in loops: print('L',l)

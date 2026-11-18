import bpy,bmesh
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
slots=[s.material.name for s in o.material_slots]; print('SLOTS',slots)
bm=bmesh.new(); bm.from_mesh(me)
seen=set(); comps={}
for f in bm.faces:
    if f.index in seen: continue
    st=[f]; c=[]; seen.add(f.index)
    while st:
        g=st.pop(); c.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); st.append(h)
    vs={v for f in c for v in f.verts}; cc=sum((v.co for v in vs),Vector())/len(vs)
    mats=sorted(set(slots[f.material_index] for f in c))
    ext=[max(v.co[i] for v in vs)-min(v.co[i] for v in vs) for i in range(3)]
    print('C',len(c),[round(x,2) for x in cc],[round(x,2) for x in ext],mats)

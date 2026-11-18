import bpy, bmesh
from mathutils import Vector
from collections import defaultdict
for ob in bpy.data.collections['OR_skirt_base_course_20261031or'].objects:
    me=ob.data; mw=ob.matrix_world
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    isl=[];seen=set()
    # count islands
    for v in bm.verts:
        if v.index in seen: continue
        st=[v]; comp=[]
        while st:
            x=st.pop()
            if x.index in seen: continue
            seen.add(x.index); comp.append(x.index); st+= [e.other_vert(x) for e in x.link_edges]
        isl.append(comp)
    # per island: top z at its extreme verts; find islands' top verts close (<0.6 m xy) to another island's top verts with dz>0.03
    tops=[]
    for ii,comp in enumerate(isl):
        zs=[(mw@me.vertices[i].co) for i in comp]; zmax=max(p.z for p in zs)
        # top verts: those whose z is the max within their xy column
        col=defaultdict(list)
        for p in zs: col[(round(p.x,2),round(p.y,2))].append(p)
        for k,ps in col.items(): tops.append((ii,max(ps,key=lambda p:p.z)))
    steps=[]
    for a in range(len(tops)):
        ia,pa=tops[a]
        for b in range(a+1,len(tops)):
            ib,pb=tops[b]
            if ia==ib: continue
            if (pa.xy-pb.xy).length<0.6 and abs(pa.z-pb.z)>0.03: steps.append((round(abs(pa.z-pb.z),3),[round(x,1) for x in pa]))
    steps.sort(reverse=True)
    print('ST',ob.name[:40],'islands',len(isl),'steps',len(steps),steps[:8])

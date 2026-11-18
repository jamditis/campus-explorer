import bpy, bmesh
from mathutils import Vector
O=Vector((229.624,391.68,0));U=Vector((0.3338,0.9426,0));N=Vector((-0.9426,0.3338,0))
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith(('VW_Bohn','WA_Bohn','WB_Bohn')): continue
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    seen=set(); out=[]
    for v in bm.verts:
        if v.index in seen: continue
        isl=[];st=[v];seen.add(v.index)
        while st:
            a=st.pop();isl.append(a)
            for e in a.link_edges:
                b=e.other_vert(a)
                if b.index not in seen: seen.add(b.index);st.append(b)
        ps=[mw@a.co for a in isl]; c=sum(ps,Vector())/len(ps); q=Vector((c.x,c.y,0))-O
        t=q.dot(U); n=q.dot(N)
        if -12<t<-6 and -3<n<6:
            ts=[(Vector((p.x,p.y,0))-O).dot(U) for p in ps]
            out.append((round(t,2),round(n,2),round(min(p.z for p in ps),1),round(max(p.z for p in ps),1),round(min(ts),2),round(max(ts),2)))
    bm.free()
    for r in sorted(out): print('REM',o.name[:28],r)

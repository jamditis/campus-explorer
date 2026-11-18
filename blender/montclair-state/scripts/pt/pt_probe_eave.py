import bpy, bmesh
from mathutils import Vector
o=bpy.data.objects['PN_Feliciano_eaves_UNVERIFIED']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); seen=set(); isl=[]
for f0 in bm.faces:
    if f0 in seen: continue
    st=[f0]; cur=set()
    while st:
        f=st.pop()
        if f in cur: continue
        cur.add(f); st+=[g for e in f.edges for g in e.link_faces]
    seen|=cur; vs={v for f in cur for v in f.verts}; P=[mw@v.co for v in vs]
    lo=Vector([min(p[a] for p in P) for a in range(3)]); hi=Vector([max(p[a] for p in P) for a in range(3)])
    if lo.x<-252 and hi.x>-258 and lo.y<212 and hi.y>209.5 and lo.z<154 and hi.z>152.5: print('EAVE isl verts',len(vs),'lo',tuple(round(x,2) for x in lo),'hi',tuple(round(x,2) for x in hi))
print('EAVE total V',len(o.data.vertices))

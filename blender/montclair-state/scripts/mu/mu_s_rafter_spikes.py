# Session mu: remove the two leftover rafter tails (eave soffit+fascia+rafter object) under the S eave return (u 2.37-3.19, below the return box) that read as dark spikes in the close-up.
import bpy, bmesh
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
o=[x for x in bpy.data.objects if x.name.startswith('School of Communication and Media eave soffit + fascia + rafter')][0]; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data)
sel=[f for f in bm.faces if (lambda c: 2.37<c.dot(t)<3.19 and 20.0<c.dot(n)<23.6 and 146.2<c.z<147.0)(mw@f.calc_center_median())]
# grow to whole linked islands so no half-tails remain, but only islands entirely inside u 2.3-3.3
isl=set(); out=[]
for f in sel:
    if f in isl: continue
    st=[f]; cur={f}
    while st:
        g=st.pop()
        for e in g.edges:
            for h in e.link_faces:
                if h not in cur: cur.add(h); st.append(h)
    us=[(mw@v.co).dot(t) for g in cur for v in g.verts]
    print('ISL',len(cur),'u',round(min(us),3),round(max(us),3))
    if min(us)>2.30 and max(us)<3.30: isl|=cur
    else: out.append(len(cur))
bmesh.ops.delete(bm,geom=list(isl),context='FACES'); bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(o.data); o.data.update(); bm.free(); print('SPIKES removed faces',len(isl),'skipped islands',out)
print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')

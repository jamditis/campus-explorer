# Session mv: barrel-tile stub on top of the S eave return (mu "not fixed"). Find tile islands whose centroid lies on the
# return (u 2.36-3.25, w 20.8-23.2) and remove them (dry run with --dry).
import bpy, bmesh, sys
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
DRY='--dry' in sys.argv
o=bpy.data.objects['School of Communication and Media barrel tile eave course']; mw=o.matrix_world
print('users',o.data.users)
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
seen=set(); kill=[]
for f in bm.faces:
    if f.index in seen: continue
    isl=[]; st=[f]; seen.add(f.index)
    while st:
        g=st.pop(); isl.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); st.append(h)
    vs={v for g in isl for v in g.verts}
    c=sum((mw@v.co for v in vs),Vector())/len(vs)
    u=c.dot(t); w=c.dot(n)
    if 1.9<u<3.4 and 20.5<w<23.4 and 146.6<c.z<147.6:
        us=[(mw@v.co).dot(t) for v in vs]; ws=[(mw@v.co).dot(n) for v in vs]
        print('isl nf',len(isl),'c u',round(u,3),'w',round(w,3),'z',round(c.z,3),'u',round(min(us),2),round(max(us),2),'w',round(min(ws),2),round(max(ws),2))
        if u>2.36: kill.extend(isl)
print('kill faces',len(kill))
if not DRY and kill:
    vk={v for g in kill for v in g.verts}
    bmesh.ops.delete(bm,geom=list(kill),context='FACES')
    loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.to_mesh(o.data); o.data.update(); print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')
bm.free()

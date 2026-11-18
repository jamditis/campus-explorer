# ws157b on ws157a: flatten the WS157 brick infill into clean planes (cells within ±0.35 m of the main wall depth snap to one plane,
# recessed porch cells keep their own depth snapped per 0.1 m), drop islands < 6 cells (the stepped '+' bits by the screen block).
import bpy, bmesh, resource, statistics
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
C=(W_N+W_S+E_N+E_S)/4; A=W_N; u=(E_N-W_N).normalized(); n=Vector((u.y,-u.x)); L=(E_N-W_N).length
if ((W_N+E_N)/2-C).dot(n)<0: n=-n
n3=Vector((n.x,n.y,0))
o=bpy.data.objects['WS157_Freeman_N_entrance_block_brick_infill_UNVERIFIED']; me=o.data
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
# islands
seen=set(); kill=[]
for f in bm.faces:
    if f.index in seen: continue
    comp=[]; st=[f]; seen.add(f.index)
    while st:
        g=st.pop(); comp.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index not in seen: seen.add(h.index); st.append(h)
    if len(comp)<6: kill+=comp
bmesh.ops.delete(bm,geom=kill,context='FACES'); print('FIX157B islands removed faces',len(kill))
def dd(p): return (Vector((p.x,p.y))-A).dot(n)
fd={f:dd(f.calc_center_median()) for f in bm.faces}
dmed=statistics.median(fd.values()); print('FIX157B dmed',round(dmed,3),'n',len(fd))
# split shared verts so each face can move independently, then snap
bmesh.ops.split_edges(bm,edges=bm.edges[:])
bm.faces.ensure_lookup_table()
nmain=0
for f in bm.faces:
    d=dd(f.calc_center_median())
    tgt=dmed if abs(d-dmed)<=0.35 else round(d*10)/10.0
    if tgt==dmed: nmain+=1
    for v in f.verts: v.co+= n3*(tgt-dd(v.co))
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.004)
bm.to_mesh(me); bm.free(); me.update()
print('FIX157B faces',len(me.polygons),'on main plane',nmain)
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws157b.blend',copy=True)
print('SAVED_WS157B RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

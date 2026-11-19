# W54: the CCOM dock apron (CCOM_dock_apron_20261014jf3, asphalt) stands 8-75 cm proud of the terrain lawn along its
# SE front edge (x 8.9-12, y ~-38.5..-39.2) and its E edge (x 11.6-15.2, y -39..-21), showing a dark slab face (probe226k).
# ws46 found the apron itself sits +0.5-0.7 m over the DTM (built-up fill, real DTM drop at x~18). Design read: an asphalt
# apron on fill meets the lawn with a graded grass shoulder, not an exposed slab edge (no curb/wall seen there in the ortho;
# UNVERIFIED by photo). New object, nothing moved (AGENTS rule 6: paving not lowered): a lawn shoulder strip from each
# boundary vertex (2 cm in under the slab, 1 cm below its top) out along the outward normal to the terrain, width
# clamp(2.5 x drop, 0.5, 1.8) m (<= ~1:2.5 bank), outer edge 1 cm above the terrain. Lawn material WS70_berm_lawn_ortho_matched (as the ws224 verge; the terrain ortho material would paint the apron's own grey onto the strip).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']; M=ap.matrix_world; R=M.to_3x3(); me=ap.data
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
sv=[m.show_viewport for m in t.modifiers]
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); tm=e.to_mesh()
B=BVHTree.FromPolygons([v.co.copy() for v in tm.vertices],[p.vertices[:] for p in tm.polygons]); e.to_mesh_clear()
for m,s in zip(t.modifiers,sv): m.show_viewport=s
def tz(x,y,z0):
    h=B.ray_cast(Vector((x,y,z0+3)),Vector((0,0,-1))); return h[0].z if h[0] else None
cnt={}
for p in me.polygons:
    if (R@p.normal).z>0.3:
        for k in p.edge_keys: cnt[k]=cnt.get(k,0)+1
adj={}
for (a,b),c in cnt.items():
    if c==1: adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
# order the boundary loop
start=next(iter(adj)); loop=[start]; prev=None; cur=start
while True:
    nx=[n for n in adj[cur] if n!=prev]
    if not nx or nx[0]==start: break
    prev,cur=cur,nx[0]; loop.append(cur)
W=[M@me.vertices[i].co for i in loop]
cen=sum(W,Vector())/len(W)
def outn(k):
    a=W[k-1]; b=W[(k+1)%len(W)]; d=b-a; d.z=0; n=Vector((d.y,-d.x,0)).normalized()
    return n if n.dot(W[k]-cen)>0 else -n
sel=[k for k,w in enumerate(W) if (w.x>8.8 and w.y<-38.2) or (w.x>11.5 and w.y<-20.9)]
# keep it contiguous in loop order
sel=sorted(sel); 
runs=[]; 
for k in sel:
    if runs and k==runs[-1][-1]+1: runs[-1].append(k)
    else: runs.append([k])
if len(runs)>1 and runs[0][0]==0 and runs[-1][-1]==len(W)-1: runs[0]=runs[-1]+runs[0]; runs.pop()
run=max(runs,key=len)
print('F226D boundary verts',len(W),'shoulder run',len(run),'from',tuple(round(c,2) for c in W[run[0]]),'to',tuple(round(c,2) for c in W[run[-1]]),flush=True)
bm=bmesh.new(); ring=[]; drops=[]
for k in run:
    w=W[k]; n=outn(k)
    z1=tz(w.x+n.x*0.3,w.y+n.y*0.3,w.z)
    if z1 is None: continue
    drop=max(0.0,w.z-z1); wid=min(1.8,max(0.5,2.5*drop)); drops.append(drop)
    q=w+n*wid; zq=tz(q.x,q.y,w.z)
    if zq is None: continue
    a=bm.verts.new(Vector((w.x-n.x*0.02,w.y-n.y*0.02,w.z-0.01)))
    m_=w+n*(wid*0.5); zm=tz(m_.x,m_.y,w.z)
    mid=bm.verts.new(Vector((m_.x,m_.y,max(zm+0.01, (w.z-0.01)*0.4+(zq+0.01)*0.6))))
    b=bm.verts.new(Vector((q.x,q.y,zq+0.01)))
    ring.append((a,mid,b))
for (a0,m0,b0),(a1,m1,b1) in zip(ring,ring[1:]):
    for f in (bm.faces.new((a0,m0,m1,a1)),bm.faces.new((m0,b0,b1,m1))):
        f.normal_update()
        if f.normal.z<0: f.normal_flip()
nm='WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED'
old=bpy.data.objects.get(nm)
if old: bpy.data.objects.remove(old)
m2=bpy.data.meshes.new('WS226_CCOM_dock_apron_lawn_shoulder'); bm.to_mesh(m2); bm.free()
uv=m2.uv_layers.new(name='ortho')
for l in m2.loops:
    c=m2.vertices[l.vertex_index].co; uv.data[l.index].uv=((c.x+250)/500,(c.y+250)/500)
for p in m2.polygons: p.use_smooth=True
o=bpy.data.objects.new(nm,m2); o.data.materials.append(bpy.data.materials['WS70_berm_lawn_ortho_matched'])
for c in ap.users_collection: c.objects.link(o)
print('F226D shoulder faces',len(m2.polygons),'area %.2f m2'%sum(p.area for p in m2.polygons),'drop max %.2f mean %.2f'%(max(drops),sum(drops)/len(drops)),'mat','WS70_berm_lawn_ortho_matched',flush=True)

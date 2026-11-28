# ws271a (merge208 CHAIN, on ws270b): W72 leftovers on the College Ave / Lot 33 paving top outline.
# probe271a found the "sawtooth" at the SW corner (x -387...-374, y -44...-38) and the "dark notch" at the N edge by the police
# south walk W end (x -358...-354, y -23...-21) are reflex notches in the asphalt top outline: interior 1 m grid verts sit on the
# boundary between the outline verts, and a 0.6 m vertical asphalt skirt hangs from them, so each notch shows as a dark slit.
# Fix: move each notch vertex b onto the straight segment between its outline neighbours a and c (z interpolated, never below the
# evaluated ground + 3 cm), and its skirt bottom b' onto the a'-c' interpolation, so the outline and its shoulder run straight.
# Faces touching b' take the shoulder material if a' and c' are shoulders. No terrain edits (AGENTS.md rule 6).
import bpy, bmesh, numpy as np, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws271')
TAG='F271A'; OB=bpy.data.objects; NAME='WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED'
WIN=[(-387.5,-373.5,-44,-38),(-358,-354,-23,-21)]
GN=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam')
gobs=[o for o in OB if o.type=='MESH' and o.name.startswith(GN)]
for o in gobs:
    for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); GT=[]
for o in gobs:
    oe=o.evaluated_get(dg); me=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not any(-392<v.co.x<-350 and -48<v.co.y<-18 for v in f.verts)],context='FACES')
    GT.append(BVHTree.FromBMesh(bm)); bm.free(); oe.to_mesh_clear()
for o in gobs:
    for m in o.modifiers: m.show_viewport=False
def gz(x,y):
    b=None
    for t in GT:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (b is None or r[0].z>b): b=r[0].z
    return b
pav=OB[NAME]; me=pav.data; mw=pav.matrix_world
assert mw==__import__('mathutils').Matrix.Identity(4)
mats=[m.name if m else '' for m in me.materials]; SH=mats.index('North_ground_ortho2020.001')
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
def topset(): return set(v for f in bm.faces if f.normal_update() or True if f.normal.z>0.3 and f.material_index==0 for v in f.verts)
def loop_notches():
    top=set()
    for f in bm.faces:
        f.normal_update()
        if f.normal.z>0.3 and f.material_index==0: top.update(f.verts)
    E={}
    for f in bm.faces:
        if f.normal.z>0.3 and f.material_index==0:
            for e in f.edges: E[e]=E.get(e,0)+1
    bd=[e for e,c in E.items() if c==1]
    adj={}
    for e in bd:
        a,b=e.verts; adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    s=bd[0].verts[0]; L=[s]; prev=None; cur=s
    while True:
        n=[x for x in adj[cur] if x is not prev][0]
        if n is s: break
        prev,cur=cur,n; L.append(n)
    P=np.array([(v.co.x,v.co.y) for v in L]); A=0.5*(np.dot(P[:,0],np.roll(P[:,1],-1))-np.dot(P[:,1],np.roll(P[:,0],-1)))
    if A<0: L=L[::-1]
    out=[]; n=len(L)
    for k in range(n):
        a,b,c=L[k-1],L[k],L[(k+1)%n]
        if not any(x0<b.co.x<x1 and y0<b.co.y<y1 for x0,x1,y0,y1 in WIN): continue
        u=(b.co-a.co).xy; w=(c.co-b.co).xy; cr=u.x*w.y-u.y*w.x
        if cr<0 and 0.5*abs(cr)<1.2 and 0.5*abs(cr)>0.02: out.append((a,b,c,0.5*abs(cr)))
    return top,out
def bottom(v,top):
    c=[e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in top and e.other_vert(v).co.z<v.co.z-0.02]
    return min(c,key=lambda x:(x.co.xy-v.co.xy).length) if c else None
moved=0
for it in range(12):
    top,out=loop_notches()
    if not out: break
    done=set()
    for a,b,c,A in out:
        if b in done or a in done or c in done: continue
        ab,bb,cb=bottom(a,top),bottom(b,top),bottom(c,top)
        d=(c.co-a.co).xy; t=max(0,min(1,((b.co-a.co).xy.dot(d))/d.length_squared))
        nx=a.co.lerp(c.co,t); g=gz(nx.x,nx.y)
        if g is not None and nx.z<g+0.03: nx.z=g+0.03
        old=b.co.copy(); upf=[f for f in b.link_faces if f.material_index==0 and f.normal.z>0.3]
        for fr in (1.0,0.75,0.5,0.25,0.0):
            b.co=old.lerp(nx,fr)
            for f in upf: f.normal_update()
            if all(f.normal.z>0.3 for f in upf): break
        if fr<1.0: print(TAG,'flip guard: move scaled to',fr,flush=True)
        nx=b.co.copy()
        if fr==0.0: done.add(b); continue
        if bb is not None and ab is not None and cb is not None:
            bb.co=bb.co.lerp(ab.co.lerp(cb.co,t),fr)
            if any(f.material_index==SH for f in ab.link_faces) and any(f.material_index==SH for f in cb.link_faces):
                for f in bb.link_faces: f.material_index=SH
        print(TAG,'it',it,'b',tuple(round(x,2) for x in old),'->',tuple(round(x,2) for x in nx),'A',round(A,3),'bottom',bb is not None,flush=True)
        done.update((a,b,c)); moved+=1
top,out=loop_notches()
print(TAG,'moved',moved,'remaining notches in windows',[(tuple(round(x,2) for x in b.co),round(A,3)) for a,b,c,A in out],flush=True)
# clearance check of all top verts in the windows
bad=[v for v in top if any(x0-1<v.co.x<x1+1 and y0-1<v.co.y<y1+1 for x0,x1,y0,y1 in WIN) and (gz(v.co.x,v.co.y) or -1e9)>v.co.z-0.025]
print(TAG,'top verts in windows below ground+2.5cm',len(bad),flush=True)
bm.normal_update()
for k in range(6):
    dn=[f for f in bm.faces if f.material_index==0 and f.normal.z<-0.3]
    if not dn: break
    f=dn[0]; e=min(f.edges,key=lambda e:e.calc_length()); keep=max(e.verts,key=lambda v:len(v.link_faces))
    print(TAG,'collapse flipped sliver',tuple(round(x,2) for x in f.calc_center_median()),'edge',round(e.calc_length(),3),flush=True)
    bmesh.ops.pointmerge(bm,verts=list(e.verts),merge_co=keep.co.copy()); bm.normal_update()
down=[f for f in bm.faces if f.material_index==0 and f.normal.z<-0.3]
print(TAG,'downward asphalt faces',len(down),[(tuple(round(x,2) for x in f.calc_center_median()),round(f.calc_area(),3),sum(v in top for v in f.verts),len(f.verts)) for f in down],flush=True)
bm.to_mesh(me); bm.free(); me.update()
pav['ws271a']='SW-corner sawtooth + N-edge notch: reflex outline verts moved onto the outline segment'

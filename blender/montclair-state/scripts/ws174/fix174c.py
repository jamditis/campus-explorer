# ws174c: UNIFY #81 (found in ws174 review) — 2.1 m GAP across the whole Normal Ave W road at the WS163/WS110 joint (WS163 ends at t -0.82,
# WS110 starts at t 1.25..1.43 on a skewed ring), lawn showing through; WS110 sits ~0.15 m higher. Fill with bridge strips (same materials)
# that share both end rings exactly: carriageway, S/N curb (top+front+back faces), S walk, N walk (WS163 3.2 m walk -> WS110 verge+walk, concrete, UNVERIFIED).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for o in [o for o in OB if o.name.startswith('WS174_junction_bridge')]: OB.remove(o)
def verts(name,tsel,ssel):
    o=next(o for o in OB if o.name.startswith(name)); mw=o.matrix_world; out=[]
    for v in o.data.vertices:
        w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
        if tsel(t) and ssel(s): out.append((round(s,3),w.x,w.y,w.z))
    return o,out
def row(pts,level='top'):
    g={}
    for s,x,y,z in pts: g.setdefault(s,[]).append((x,y,z))
    r=[]
    for s in sorted(g):
        zs=[p[2] for p in g[s]]; z=max(zs) if level=='top' else min(zs); x,y=g[s][0][0],g[s][0][1]; r.append((s,x,y,z))
    return r
def resample(r,n):
    S=np.array([p[0] for p in r]); P=np.array([p[1:] for p in r]); u=(S-S[0])/(S[-1]-S[0]) if len(S)>1 else np.zeros(1)
    U=np.linspace(0,1,n); return [tuple(np.interp(uu,u,P[:,k]) for k in range(3)) for uu in U]
def strip(nm,mat,ra,rb,skirt=0.0):
    n=max(len(ra),len(rb)); a=resample(ra,n); b=resample(rb,n)
    bm=bmesh.new(); VA=[bm.verts.new(p) for p in a]; VB=[bm.verts.new(p) for p in b]
    for i in range(n-1): bm.faces.new((VA[i],VA[i+1],VB[i+1],VB[i]))
    if skirt>0:
        for side in (0,n-1):
            a2=bm.verts.new((VA[side].co.x,VA[side].co.y,VA[side].co.z-skirt)); b2=bm.verts.new((VB[side].co.x,VB[side].co.y,VB[side].co.z-skirt))
            bm.faces.new((VA[side],VB[side],b2,a2))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    for f in bm.faces:
        if f.normal.z< -0.5: f.normal_flip()
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=OB.new(nm,me); bpy.context.scene.collection.objects.link(o); return o
def quad(nm,mat,p):   # list of 4-pt faces
    bm=bmesh.new()
    for f in p: bm.faces.new([bm.verts.new(c) for c in f])
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-4)
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=OB.new(nm,me); bpy.context.scene.collection.objects.link(o); return o
E163=lambda t: t>-0.9 and t<-0.7
E110=lambda t: 1.2<t<1.5
made=[]
# carriageway
oa,pa=verts('WS163_NormalAve_W_carriageway',E163,lambda s:-11.5<s<0.05); ob,pb=verts('WS110_NormalAve_carriageway',E110,lambda s:-11.5<s<0.3)
made.append(strip('WS174_junction_bridge_carriageway_UNIFY81',oa.data.materials[0],row(pa),row(pb),skirt=0.10))
# curbs (box faces)
for side,sa,sb in (('S',lambda s:-11.5<s<-11.0,lambda s:-11.5<s<-11.0),('N',lambda s:-0.05<s<0.25,lambda s:0.1<s<0.55)):
    oa,pa=verts('WS163_NormalAve_W_%s_curb'%side,E163,sa); ob,pb=verts('WS110_NormalAve_curb',E110,sb)
    ta=row(pa,'top'); ba=row(pa,'bot'); tb=row(pb,'top'); bb=row(pb,'bot')
    P=lambda r,i: tuple(r[i][1:])
    F=[(P(ta,0),P(ta,-1),P(tb,-1),P(tb,0)),(P(ba,0),P(ta,0),P(tb,0),P(bb,0)),(P(ta,-1),P(ba,-1),P(bb,-1),P(tb,-1))]
    made.append(quad('WS174_junction_bridge_%s_curb_UNIFY81'%side,oa.data.materials[0],F))
# S walk
oa,pa=verts('WS163_NormalAve_W_S_sidewalk',E163,lambda s:-13.2<s<-11.2); ob,pb=verts('WS110_NormalAve_sidewalk',E110,lambda s:-13.2<s<-11.2)
made.append(strip('WS174_junction_bridge_S_walk_UNIFY81',oa.data.materials[0],row(pa),row(pb),skirt=0.12))
# N walk: WS163 walk 0.18..3.38 -> WS110 curb back (0.48) + walk 1.979..3.479
oa,pa=verts('WS163_NormalAve_W_N_sidewalk',E163,lambda s:0.1<s<3.5); ob,pb=verts('WS110_NormalAve_sidewalk',E110,lambda s:1.5<s<3.6)
oc,pc=verts('WS110_NormalAve_curb',E110,lambda s:0.4<s<0.55)
rb=row(pc,'top')+row(pb,'top')
made.append(strip('WS174_junction_bridge_N_walk_UNVERIFIED_UNIFY81',oa.data.materials[0],row(pa),rb,skirt=0.12))
for o in made: print('FIX174c',o.name,len(o.data.vertices),'z',round(min((o.matrix_world@v.co).z for v in o.data.vertices),3),round(max((o.matrix_world@v.co).z for v in o.data.vertices),3),flush=True)
# sink lawn/ground under the bridges
bv=[BVHTree.FromPolygons([v.co.copy() for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in made]
def cz(x,y):
    z=None
    for b in bv:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
        if h[0] is not None and (z is None or h[0].z>z): z=h[0].z
    return z
for n in ['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED','WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']:
    o=OB.get(n)
    if not o: continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
        if not (-3.0<t<3.5 and -14<s<4.5): continue
        best=None
        for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
            z=cz(w.x+dx,w.y+dy)
            if z is not None and (best is None or z<best): best=z
        if best is not None and w.z>best-0.10: w.z=best-0.12; v.co=mi@w; k+=1
    o.data.update(); print('FIX174c sunk',n,k,flush=True)
# paving proxy: append bridge tops so GN scatter masks treat them as paving (if the proxy exists)
px=OB.get('WS113_paving_tops_proxy')
if px:
    bm=bmesh.new(); bm.from_mesh(px.data); mi=px.matrix_world.inverted()
    for o in made:
        for p in o.data.polygons:
            if p.normal.z>0.7: bm.faces.new([bm.verts.new(mi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    bm.to_mesh(px.data); bm.free(); px.data.update(); print('FIX174c proxy faces',len(px.data.polygons),flush=True)

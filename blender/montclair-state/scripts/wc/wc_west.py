"""wc west (RAISE-only, plus under-slab verts within 1.5 m of the walk edge lifted to slab -5 cm (wb_under method) version; first lower-only dry run showed the walk is 3-11 cm PROUD on that side, not sunken): the 435 walk's west (RZ2) side at x44-58,y309-317 sits up to ~16 cm BELOW the lawn, so the soil strip shows as a
tan up-slope in the W eye. Lower-only: RZ2 and WT verts beside the walk (not under any slab) that are above walk top -1.5 cm
go to walk top -1.5 cm within 0.8 m, fading back to their own z by 2.0 m (cap 20 cm). WT kept >=1 cm under RZ2 where RZ2
covers. Then RZ2 boundary verts exposed above WT lowered (wb_rz_edge method), grass re-snapped, 435 soil strip re-seated."""
import bpy,numpy as np,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from collections import Counter
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
WN='QS_footway_313027435_UNVERIFIED'
SLn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
GRD=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; RZ=O[[n for n in O.keys() if n.startswith('RZ2_')][0]]
BX=(43,59,308.5,317.5); D_FULL=0.8; D_OUT=2.0; DROP=0.025; CAP=0.15
def dg(): return bpy.context.evaluated_depsgraph_get()
def mesh(o):
    e=o.evaluated_get(dg()); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; N=[(o.matrix_world.to_3x3()@p.normal).normalized() for p in m.polygons]; e.to_mesh_clear(); return V,P,N
def bvh(o): V,P,_=mesh(o); return BVHTree.FromPolygons(V,P)
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
SL=[bvh(O[n]) for n in SLn]
V,P,N=mesh(O[WN]); ec=Counter(); pts=[]
for p,q in zip(P,N):
    if q.z<0.5: continue
    for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
for (a,b),c in ec.items():
    if c!=1: continue
    A,B=V[a],V[b]; n=max(1,int((B-A).length/0.1))
    for k in range(n+1):
        q=A+(B-A)*(k/n)
        if BX[0]-2<=q.x<=BX[1]+2 and BX[2]-2<=q.y<=BX[3]+2: pts.append(q)
kd=KDTree(len(pts))
for i,p in enumerate(pts): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
def exposure(tag):
    G=[bvh(O[n]) for n in GRD]; ex=[]
    for i in range(0,len(pts),3):
        p=pts[i]
        if not (BX[0]<=p.x<=BX[1] and BX[2]<=p.y<=BX[3]): continue
        for ang in np.linspace(0,2*np.pi,12,endpoint=False):
            x=p.x+0.3*np.cos(ang); y=p.y+0.3*np.sin(ang)
            if top(SL,x,y) is not None: continue
            g=top(G,x,y)
            if g is not None: ex.append(p.z-g)
            break
    ex=np.array(ex); r=dict(n=len(ex),p10=round(float(np.percentile(ex,10)),3),p50=round(float(np.median(ex)),3),p90=round(float(np.percentile(ex,90)),3),min=round(float(ex.min()),3),max=round(float(ex.max()),3),n_lt_m3=int((ex<-0.03).sum()),n_gt5=int((ex>0.05).sum()))
    print('EXPOSURE',tag,r,flush=True); return r
rep={'exp0':exposure('before')}
PRE={}; 
for o in (RZ,WT):
    me=o.data; mw=o.matrix_world; mi=mw.inverted(); PRE[o.name]=np.array([v.co[:] for v in me.vertices]); np.save(f'{R}/data/wc/{o.name[:2]}_pre_wcwest.npy',PRE[o.name])
    k=0; mx=0
    for v in me.vertices:
        c=mw@v.co
        if not (BX[0]<=c.x<=BX[1] and BX[2]<=c.y<=BX[3]): continue
        su=top(SL,c.x,c.y)
        co,i,d=kd.find(Vector((c.x,c.y,0)))
        if su is not None:
            if d>1.5 or c.z>=su-0.05: continue
            dz=min(su-0.05-c.z,CAP+0.1); c.z+=dz; v.co=mi@c; k+=1; mx=max(mx,dz); continue
        if d>D_OUT: continue
        tgt=pts[i].z-DROP
        if c.z>=tgt: continue
        w=0.0 if d<=D_FULL else (d-D_FULL)/(D_OUT-D_FULL); w=w*w*(3-2*w)
        dz=min((tgt-c.z)*(1-w),CAP)
        if dz>0.002: c.z+=dz; v.co=mi@c; k+=1; mx=max(mx,dz)
    me.update(); rep['raise_'+o.name[:2]]=[k,round(mx,3)]; print('RAISE',o.name[:2],k,round(mx,3),flush=True)
bpy.context.view_layer.update()
# WT under RZ2 -1 cm
RB=bvh(RZ); mw=WT.matrix_world; mi=mw.inverted(); k=0
for v in WT.data.vertices:
    c=mw@v.co
    if not (BX[0]-1<=c.x<=BX[1]+1 and BX[2]-1<=c.y<=BX[3]+1): continue
    r=top([RB],c.x,c.y)
    if r is not None and c.z>r-0.01 and top(SL,c.x,c.y) is None: c.z=r-0.01; v.co=mi@c; k+=1
WT.data.update(); bpy.context.view_layer.update(); rep['wt_under_rz']=k; print('WTUNDER',k,flush=True)
# RZ2 boundary verts exposed above WT -> WT+0.5cm (lower only)
V2,P2,_=mesh(RZ); ec=Counter()
for p in P2:
    for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
bnd={i for e,c in ec.items() if c==1 for i in e}; WB=bvh(WT); mw=RZ.matrix_world; mi=mw.inverted(); k=0
for i in bnd:
    c=mw@RZ.data.vertices[i].co
    if not (BX[0]-2<=c.x<=BX[1]+2 and BX[2]-2<=c.y<=BX[3]+2): continue
    w=top([WB],c.x,c.y)
    if w is not None and c.z>w+0.005: c.z=w+0.005; RZ.data.vertices[i].co=mi@c; k+=1
RZ.data.update(); bpy.context.view_layer.update(); rep['rz_edge']=k; print('RZEDGE',k,flush=True)
# pokes
G=[bvh(O[n]) for n in GRD]; pk=0
for x in np.arange(BX[0],BX[1],0.25):
    for y in np.arange(BX[2],BX[3],0.25):
        s=top(SL,x,y)
        if s is None: continue
        g=top(G,x,y)
        if g is not None and g>s-0.005: pk+=1
rep['pokes']=pk; print('POKES',pk,flush=True)
for it in range(3):
    if pk==0: break
    G=[bvh(O[n]) for n in GRD]; fixed=0
    for o in (RZ,WT):
        B=bvh(o); mw=o.matrix_world
        for x in np.arange(BX[0],BX[1],0.25):
            for y in np.arange(BX[2],BX[3],0.25):
                s_=top(SL,x,y)
                if s_ is None: continue
                h=B.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
                if h[0] is None or h[0].z<=s_-0.005: continue
                for vi in o.data.polygons[h[2]].vertices:
                    v=o.data.vertices[vi]; pz=PRE[o.name][vi][2]
                    if v.co.z>pz+1e-5: v.co.z=max(pz,v.co.z-(h[0].z-s_+0.012)); fixed+=1
        o.data.update()
    bpy.context.view_layer.update()
    G=[bvh(O[n]) for n in GRD]; pk=0
    for x in np.arange(BX[0],BX[1],0.25):
        for y in np.arange(BX[2],BX[3],0.25):
            s_=top(SL,x,y)
            if s_ is None: continue
            g=top(G,x,y)
            if g is not None and g>s_-0.005: pk+=1
    print('BACKOFF',it,fixed,'POKES',pk,flush=True); rep['pokes_b%d'%it]=pk
rep['exp1']=exposure('after')
G=[bvh(O[n]) for n in GRD]; kg=0
for name in [n for n in O.keys() if 'grass_points' in n and n[:2] in ('QS','QV','RZ','RG')]:
    g=O[name]; m=g.matrix_world; mi2=m.inverted()
    for v in g.data.vertices:
        c=m@v.co
        if not (BX[0]-1<=c.x<=BX[1]+1 and BX[2]-1<=c.y<=BX[3]+1): continue
        z=top(G,c.x,c.y)
        if z is None: continue
        if top(SL,c.x,c.y) is not None:
            if c.z>z-0.15: c.z=z-0.2; v.co=mi2@c; kg+=1
        elif abs(c.z-z)>0.01: c.z=z; v.co=mi2@c; kg+=1
    g.data.update()
rep['grass']=kg; print('GRASS',kg,[n for n in O.keys() if 'grass_points' in n],flush=True)
t=O[WN.replace('QS_footway_','QT_soil_edge_')]; S=bvh(O[WN]); mw=t.matrix_world; inv=mw.inverted(); k=0
for p in t.data.polygons:
    vi=list(p.vertices); ws=[mw@t.data.vertices[i].co for i in vi]
    if not any(BX[0]-1<=w.x<=BX[1]+1 and BX[2]-1<=w.y<=BX[3]+1 for w in ws): continue
    d=[S.find_nearest(w)[3] for w in ws]
    for j in np.argsort(d)[2:]:
        w=ws[j]; z=top(G,w.x,w.y)
        if z is None: continue
        if abs(w.z-(z+0.01))>0.003: t.data.vertices[vi[j]].co=inv@Vector((w.x,w.y,z+0.01)); k+=1
t.data.update(); rep['reseat']=k; print('RESEAT',k,flush=True)
json.dump(rep,open(f'{R}/data/wc/west_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)

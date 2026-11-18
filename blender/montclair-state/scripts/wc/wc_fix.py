"""wc: ease WT+WF lawn up beside walk 436's north end (and 435's NE end) at Richardson west, box x56-72,y316-327.
Raise-only to walk top -2.5 cm within 1 m (fade to 2.6 m, cap 30 cm); verts under the walks lifted to slab -5 cm.
Crack-safe overlap (WT y<=320.4, WF y>=318.5): WT raise fades 1->0 over y319.4-320.4 (its N edge unmoved), WF raise
fades 0->1 over y318.5-319.5 (its S edge unmoved), so each sheet's edge stays tucked under the other. Then clamp
slab pokes, re-snap grass, re-seat soil strips."""
import bpy,numpy as np,json,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from collections import Counter
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects
WALK=['QS_footway_313027436_UNVERIFIED','QS_footway_313027435_UNVERIFIED']
SLn=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
GRD=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
WT='WT_richardson_west_LiDAR_patch_UNVERIFIED'; WF='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
BX=(56,72,316,327); D_FULL=1.0; D_OUT=2.6; LIFT=0.025; CAP=0.30
def dg(): return bpy.context.evaluated_depsgraph_get()
def mesh(o):
    e=o.evaluated_get(dg()); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; N=[(o.matrix_world.to_3x3()@p.normal).normalized() for p in m.polygons]; e.to_mesh_clear(); return V,P,N
def bvh(o): V,P,_=mesh(o); return BVHTree.FromPolygons(V,P)
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
SL=[bvh(O[n]) for n in SLn]
pts=[]
for wn in WALK:
    V,P,N=mesh(O[wn]); ec=Counter()
    for p,q in zip(P,N):
        if q.z<0.5: continue
        for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
    for (a,b),c in ec.items():
        if c!=1: continue
        A,B=V[a],V[b]; n=max(1,int((B-A).length/0.1))
        for k in range(n+1):
            q=A+(B-A)*(k/n)
            if BX[0]-3<=q.x<=BX[1]+3 and BX[2]-3<=q.y<=BX[3]+3: pts.append(q)
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
    ex=np.array(ex); r=dict(n=len(ex),p50=round(float(np.median(ex)),3),p90=round(float(np.percentile(ex,90)),3),max=round(float(ex.max()),3),n_gt5=int((ex>0.05).sum()),n_neg=int((ex<-0.01).sum()))
    print('EXPOSURE',tag,r,flush=True); return r
def pokes(tag):
    G=[bvh(O[n]) for n in GRD]; c=0; mx=0; L=[]
    for x in np.arange(BX[0]-1,BX[1]+1,0.25):
        for y in np.arange(BX[2]-1,BX[3]+1,0.25):
            s=top(SL,x,y)
            if s is None: continue
            g=top(G,x,y)
            if g is not None and g>s-0.005: c+=1; mx=max(mx,g-s); L.append((x,y,g-s))
    print('POKES',tag,c,round(mx,3),flush=True); return L
rep={'exp0':exposure('before'),'pk0':len(pokes('before'))}
def fy(n,y):
    if n==WT: f=1.0 if y<=319.4 else max(0.0,(320.4-y)/1.0)
    else: f=0.0 if y<=318.5 else min(1.0,(y-318.5)/1.0)
    return f*f*(3-2*f)
G0=[bvh(O[n]) for n in GRD]; PRE={}
for n in (WT,WF):
    o=O[n]; me=o.data; mw=o.matrix_world; mi=mw.inverted()
    PRE[n]=np.array([v.co[:] for v in me.vertices]); np.save(f'{R}/data/wc/{n[:2]}_pre_wc.npy',PRE[n])
    cv=cu=0; mx=0
    for v in me.vertices:
        c=mw@v.co
        if not (BX[0]<=c.x<=BX[1] and BX[2]<=c.y<=BX[3]): continue
        f=fy(n,c.y)
        if f<=0: continue
        g=top(G0,c.x,c.y)
        if g is not None and c.z<g-0.05: continue
        s=None
        for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            t=top(SL,c.x+dx,c.y+dy)
            if t is not None: s=t if s is None else max(s,t)
        if top(SL,c.x,c.y) is not None:
            tgt=s-0.05; kind='u'
        else:
            co,i,d=kd.find(Vector((c.x,c.y,0)))
            if d>D_OUT: continue
            w=0.0 if d<=D_FULL else (d-D_FULL)/(D_OUT-D_FULL); w=w*w*(3-2*w)
            tgt=(pts[i].z-LIFT)*(1-w)+c.z*w; kind='v'
            if s is not None: tgt=min(tgt,s-0.015)
        dz=min(max(0.0,(tgt-c.z)*f),CAP)
        if dz>0.002:
            c.z+=dz; v.co=mi@c; mx=max(mx,dz)
            if kind=='u': cu+=1
            else: cv+=1
    me.update(); rep['raise_'+n[:2]]=[cv,cu,round(mx,3)]; print('RAISE',n[:2],cv,cu,round(mx,3),flush=True)
bpy.context.view_layer.update()
L=pokes('after')
for it in range(4):
    if len(L)<=rep['pk0']: break
    for n in (WT,WF):
        o=O[n]; B=bvh(o); ids={}
        for x,y,d in L:
            h=B.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
            if h[2] is None: continue
            for vi in o.data.polygons[h[2]].vertices:
                if abs(o.data.vertices[vi].co.z-PRE[n][vi][2])>1e-5: ids[vi]=max(ids.get(vi,0),d+0.012)
        for vi,d in ids.items(): o.data.vertices[vi].co.z=max(PRE[n][vi][2],o.data.vertices[vi].co.z-d)
        o.data.update()
    bpy.context.view_layer.update(); L=pokes('backoff%d'%it)
rep['pk1']=len(L); rep['exp1']=exposure('after')
G=[bvh(O[n]) for n in GRD]; kg=0
for name in [n for n in O.keys() if 'grass_points' in n and n[:2] in ('QS','QV')]:
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
rep['grass']=kg; print('GRASS',kg,flush=True)
for sn in WALK:
    t=O.get(sn.replace('QS_footway_','QT_soil_edge_'))
    if not t: continue
    S=bvh(O[sn]); mw=t.matrix_world; inv=mw.inverted(); k=0
    for p in t.data.polygons:
        vi=list(p.vertices); ws=[mw@t.data.vertices[i].co for i in vi]
        if not any(BX[0]-1<=w.x<=BX[1]+1 and BX[2]-1<=w.y<=BX[3]+1 for w in ws): continue
        d=[S.find_nearest(w)[3] for w in ws]
        for j in np.argsort(d)[2:]:
            w=ws[j]; z=top(G,w.x,w.y)
            if z is None: continue
            if abs(w.z-(z+0.01))>0.003: t.data.vertices[vi[j]].co=inv@Vector((w.x,w.y,z+0.01)); k+=1
    t.data.update(); rep['reseat_'+sn[11:20]]=k; print('RESEAT',t.name,k,flush=True)
json.dump(rep,open(f'{R}/data/wc/fix_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)
print('EXIT',flush=True)

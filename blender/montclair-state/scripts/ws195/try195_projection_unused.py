# ws195 WOBBLE W6: WS77 lot median island (Red Hawk/Kasser lot) -> clean designed outline: straight N and S sides
# (least-squares lines through the ws93 outer foot loop, ends excluded) + true circular round ends tangent to both sides
# (curbed mulch median, Joe catwalk photos 2026-11-12 show rounded curb noses on the campus lot medians; 2020 0.1 m ortho
# isl_check.png gives the sides; end radii = half local width, tips at the old extreme -> UNVERIFIED shape of the W end jog).
# Every island boundary loop (curb outer foot, curb top, inset, mulch edge) is re-projected onto the offset of the ideal outline
# at that loop's median offset, so concentric loops stay parallel; lot sheets near the foot move by the same field (ws93 pattern).
import bpy,math,os,sys
import numpy as np
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws91'); from straight91 import loops_of
from mathutils import Vector
from mathutils.kdtree import KDTree
OB=bpy.data.objects
isl=[o for o in OB if o.type=='MESH' and (o.name.startswith('WS77_lot_median_island') or o.name.startswith('WS77_')) and not o.hide_render]
isl=[o for o in isl if o.data.vertices and all(-262<(o.matrix_world@Vector(c)).x<-206 and -102<(o.matrix_world@Vector(c)).y<-74 for c in o.bound_box)]
lots=[o for o in OB if o.type=='MESH' and not o.hide_render and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill'))]
print('F195 island',[(o.name,len(o.data.vertices)) for o in isl],flush=True); print('F195 lots',[o.name for o in lots],flush=True)
main=[o for o in isl if o.name.startswith('WS77_lot_median_island')][0]
mw=main.matrix_world; W=np.array([tuple(mw@v.co) for v in main.data.vertices]); F=[list(p.vertices) for p in main.data.polygons]
L=loops_of(F); L.sort(key=lambda l:-len(l))
# outer loop = the loop with the largest xy area
def area(P): x,y=P[:,0],P[:,1]; return 0.5*abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
outer=max(L,key=lambda l:area(W[l]))
P=W[outer][:,:2]
# axis by PCA
c0=P.mean(0); u,s,vt=np.linalg.svd(P-c0); ax=vt[0]; 
if ax[0]<0: ax=-ax
nrm=np.array([-ax[1],ax[0]])
t=(P-c0)@ax; o=(P-c0)@nrm
tmin,tmax=t.min(),t.max(); core=(t>tmin+4)&(t<tmax-4)
N=core&(o>0); S=core&(o<0)
fn=np.polyfit(t[N],o[N],1); fs=np.polyfit(t[S],o[S],1)
print('F195 axis',ax,'t',tmin,tmax,'N fit',fn,'resid',np.abs(np.polyval(fn,t[N])-o[N]).max(),'S fit',fs,'resid',np.abs(np.polyval(fs,t[S])-o[S]).max(),flush=True)
# ideal outline in (t,o): N line o=fn(t), S line o=fs(t); end caps = circle tangent to both lines, tip at old extreme
def cap(tend,sgn):
    # bisector o=b(t)=(fn+fs)/2 ; half width h(t)=(fn-fs)/2 measured vertically; perpendicular dist to N line = h*cos(atan(slope))
    best=None
    for tc in np.linspace(tend-sgn*8,tend,4000):
        h=(np.polyval(fn,tc)-np.polyval(fs,tc))/2; ob=(np.polyval(fn,tc)+np.polyval(fs,tc))/2
        r=h*math.cos(math.atan((fn[0]-fs[0])/2))
        tip=tc+sgn*r
        if best is None or abs(tip-tend)<best[0]: best=(abs(tip-tend),tc,ob,r)
    return best[1:]
tcW,obW,rW=cap(tmin,-1); tcE,obE,rE=cap(tmax,1)
print('F195 caps W',tcW,obW,rW,'E',tcE,obE,rE,flush=True)
def circ_tan(tc,oc,r,f):  # tangent point of circle on line o=f(t)
    a,b=f; n_=np.array([-a,1.0])/math.hypot(a,1); d=(oc-(a*tc+b))/math.hypot(a,1)
    return np.array([tc,oc])-n_*d
pts=[]
nW,sW=circ_tan(tcW,obW,rW,fn),circ_tan(tcW,obW,rW,fs); nE,sE=circ_tan(tcE,obE,rE,fn),circ_tan(tcE,obE,rE,fs)
def seg(a,b,step=0.02):
    n=max(2,int(np.linalg.norm(b-a)/step)); return [a+(b-a)*k/n for k in range(n)]
def arc(c,r,a0,a1,step=0.02):
    if a1<a0: a1+=2*math.pi
    n=max(4,int(r*(a1-a0)/step)); return [c+r*np.array([math.cos(a0+(a1-a0)*k/n),math.sin(a0+(a1-a0)*k/n)]) for k in range(n)]
ang=lambda c,p: math.atan2(p[1]-c[1],p[0]-c[0])
cW=np.array([tcW,obW]); cE=np.array([tcE,obE])
pts+=seg(nW,nE); pts+=[p for p in arc(cE,rE,ang(cE,sE),ang(cE,nE))][::-1] if False else []
# go counter-clockwise in (t,o): S line W->E, E cap S->N, N line E->W, W cap N->S
pts=seg(sW,sE)+arc(cE,rE,ang(cE,sE),ang(cE,nE))+seg(nE,nW)+arc(cW,rW,ang(cW,nW),ang(cW,sW))
Q=np.array(pts)  # (t,o)
Qn=[]
for i in range(len(Q)):
    d=Q[(i+1)%len(Q)]-Q[i-1]; d/=np.linalg.norm(d); Qn.append([d[1],-d[0]])  # outward for CCW
Qn=np.array(Qn)
def to_xy(to): return c0+np.outer(to[:,0],ax)+np.outer(to[:,1],nrm)
QX=to_xy(Q); QNX=np.outer(Qn[:,0],ax)+np.outer(Qn[:,1],nrm)
kdq=KDTree(len(QX))
for i,p in enumerate(QX): kdq.insert(Vector((p[0],p[1],0)),i)
kdq.balance()
def sd(p):
    co,i,d=kdq.find(Vector((p[0],p[1],0))); return i,float(np.dot(np.array(p[:2])-QX[i],QNX[i]))
# per-object displacements
pts_all=[];dsp=[];per={};stats=[]
for ob_ in isl:
    m=ob_.matrix_world; Wo=[m@v.co for v in ob_.data.vertices]; Fo=[list(p.vertices) for p in ob_.data.polygons]; d={}
    for lp in loops_of(Fo):
        S_=[sd((Wo[i].x,Wo[i].y)) for i in lp]; off=float(np.median([s for _,s in S_]))
        if abs(off)>2.0: continue
        mx=0
        for (iq,s),vi in zip(S_,lp):
            # re-project: nearest ideal point, then along its normal to the loop offset
            tgt=QX[iq]+QNX[iq]*off
            dx,dy=tgt[0]-Wo[vi].x,tgt[1]-Wo[vi].y; d[vi]=(dx,dy); mx=max(mx,math.hypot(dx,dy))
            pts_all.append((Wo[vi].x,Wo[vi].y)); dsp.append((dx,dy))
        stats.append((ob_.name[:40],len(lp),round(off,3),round(mx,2)))
    per[ob_.name]=(Wo,d)
print('F195 loops',stats,flush=True)
kd=KDTree(len(pts_all))
for n,p in enumerate(pts_all): kd.insert(Vector((p[0],p[1],0)),n)
kd.balance()
def field(x,y,Rr,flat=0.05):
    co,n,dd=kd.find(Vector((x,y,0)))
    if n is None: return 0.0,0.0
    D=math.hypot(*dsp[n]); R2=max(Rr,1.5*D+0.3)
    if dd>R2: return 0.0,0.0
    f=1.0 if dd<flat else max(0.0,1-(dd-flat)/(R2-flat)); f=f*f*(3-2*f); return dsp[n][0]*f,dsp[n][1]*f
def apply(o,W,fixed,Rr,flat=0.05):
    me=o.data; inv=o.matrix_world.inverted(); nz0=[p.normal.z for p in me.polygons]; mv=0; mx=0
    for i,v in enumerate(me.vertices):
        dx,dy=fixed[i] if i in fixed else field(W[i].x,W[i].y,Rr,flat)
        if abs(dx)+abs(dy)<1e-4: continue
        v.co=inv@Vector((W[i].x+dx,W[i].y+dy,W[i].z)); mv+=1; mx=max(mx,math.hypot(dx,dy))
    me.update(); bad=0
    for it in range(3):
        fl=[p for p,z0 in zip(me.polygons,nz0) if abs(z0)>0.5 and p.normal.z*z0<0.2*abs(z0)]
        if not fl: break
        for p in fl:
            for vi in p.vertices: me.vertices[vi].co=inv@W[vi]; bad+=1
        me.update()
    print('F195',o.name[:50],'moved',mv,'max %.2f'%mx,'revert',bad,flush=True)
for o in isl:
    Wo,d=per[o.name]; apply(o,Wo,d,0.6)
for o in lots:
    m=o.matrix_world; Wl=[m@v.co for v in o.data.vertices]; apply(o,Wl,{},0.45)
# trees must stay inside
for tn in ('T_LondonPlane_L1_0245','T_SugarMaple_L1_0244','T_RedMaple_L1_0239'):
    t_=OB.get(tn)
    if t_: p=t_.matrix_world.translation; print('F195 tree',tn,'signed dist to new outline %.2f'%sd((p.x,p.y))[1],flush=True)
np.save('/workspace/nj-scenes/montclair-state/scripts/ws195/outline195.npy',QX)

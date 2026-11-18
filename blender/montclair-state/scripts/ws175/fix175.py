# ws175: UNIFY #80 — WS110 Normal Ave S curb/walk ~0.75 m S of the LiDAR edge along the whole straight run (t 32..184),
# evidence scripts/ws175/edge175.out (2017 + 2023 class-2 intensity asphalt->concrete edge vs model S face fit s=-0.01446t-11.028;
# robust median +0.75 m, bins 0.7/0.8/0.7/1.0 for t 32-72/72-112/112-152/152-184), prof175.out (10-15 cm curb rise at the same offset).
# Moves (straight-frame N): WS110 S curb + S walk + carriageway S edge + WS113 paving proxy by D110(t) (0.75; cosine to 0 over t 176..196
# where WS110 bends S — beyond the LiDAR coverage, UNVERIFIED). WS110 ground patch: band off[-4,-1.8] stretched to [-4,-1.8+D],
# band [-1.8,+1.0] compressed to [-1.8+D,+1.0] (monotonic, no folds), z clamped 4 cm under the nearest paving top in the paving zone.
# WS163 interim taper (ws174, t -12..-0.82) straightened: face to s -10.30 everywhere; ws174 bridge strips follow both ends.
import bpy, math, numpy as np
from mathutils import kdtree
OB=bpy.data.objects
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def D110(t):
    if t<0.9 or t>196: return 0.0
    if t<=176: return 0.75
    u=(t-176)/20.0; return 0.75*0.5*(1+math.cos(math.pi*u))
def Dold(t):
    if t<=-12.0: return 1.0
    if t>=-0.82: return 0.19
    u=(t+12.0)/11.18; return 0.19+(1.0-0.19)*0.5*(1+math.cos(math.pi*u))
def face(t): return -0.01446*t-11.028
def g163(s,t):  # ws174-style remap from current face (-11.30+Dold) to -10.30
    fr=-11.30+Dold(t); to=-10.30; d=to-fr
    if d<1e-6: return s
    if fr-1e-4<=s<=-5.65: return -5.65+(s+5.65)*(-5.65-to)/(-5.65-fr)
    if fr-1.78-1e-4<=s<fr: return s+d
    lb=fr-1.78
    if -14.48<=s<lb: return -14.48+(s+14.48)*(lb+d+14.48)/(lb+14.48)
    return s
def mv(o,fn):
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
        r=fn(s,t,w)
        if r is None: continue
        ds,dz=r
        if abs(ds)<1e-6 and abs(dz)<1e-6: continue
        w.x+=float(N[0]*ds); w.y+=float(N[1]*ds); w.z+=dz; v.co=mi@w; k+=1
    o.data.update(); print('FIX175',o.name[:60],'moved',k,flush=True); return k
def ob(pfx): return [o for o in OB if o.type=='MESH' and o.name.startswith(pfx)]
# 1) WS110 paving S band
def f110(s,t,w):
    off=s-face(t)
    if not (0.9<t<197 and -1.95<off<0.06): return None
    return (D110(t),0.0)
for p in ('WS110_NormalAve_curb_W11p3','WS110_NormalAve_sidewalk_ws85','WS110_NormalAve_carriageway_W11p3','WS113_paving_tops_proxy'):
    for o in ob(p): mv(o,f110)
# 2) WS163 taper straightened (t -12..-0.80)
def f163(s,t,w):
    if not (-12.05<t<-0.79 and -14.5<s<-5.6): return None
    return (g163(s,t)-s,0.0)
for p in ('WS163_NormalAve_W_carriageway','WS163_NormalAve_W_S_curb','WS163_NormalAve_W_S_sidewalk','WS163_walk_back_lawn_lip_S','WS172_frontyards_S_of_NormalAve_W','WS113_paving_tops_proxy'):
    for o in ob(p): mv(o,f163)
# 3) ws174 bridges: generic remap h (road band compressed to centre -5.65, curb/walk band shifted) at each end ring, S side only
def h(s,fr,to):
    d=to-fr
    if fr-1e-3<=s<=-5.65: return -5.65+(s+5.65)*(-5.65-to)/(-5.65-fr)
    if fr-1.95<=s<fr: return s+d
    return s
def fbr(s,t,w):
    if s>-5.65: return None
    if t<-0.5: return (h(s,-11.30+Dold(-0.82),-10.30)-s,0.0)
    if t>0.9: return (h(s,face(t),face(t)+D110(t))-s,0.0)
    return None
for o in ob('WS174_junction_bridge'):
    if '_N_' in o.name: continue
    mv(o,fbr)
# 4) WS110 ground patch band remap + clamp under paving
pav=[]
for p in ('WS110_NormalAve_curb_W11p3','WS110_NormalAve_sidewalk_ws85','WS110_NormalAve_carriageway_W11p3'):
    for o in ob(p):
        mw=o.matrix_world
        for v in o.data.vertices:
            w=mw@v.co; pav.append((w.x,w.y,w.z))
pav=np.array(pav); kd=kdtree.KDTree(len(pav))
for i,p in enumerate(pav): kd.insert((p[0],p[1],0.0),i)
kd.balance()
def fg(s,t,w):
    D=D110(t)
    if D<1e-4: return None
    off=s-face(t)
    if not (-4.0<=off<=1.0): return None
    if off<=-1.8: o2=-4.0+(off+4.0)*(2.2+D)/2.2
    else: o2=(-1.8+D)+(off+1.8)*(1.0-(-1.8+D))/2.8
    ds=o2-off; dz=0.0
    if o2>-1.8+D-0.02:
        nx=w.x+N[0]*ds; ny=w.y+N[1]*ds
        hits=kd.find_n((nx,ny,0.0),3); zt=min(pav[i][2] for _,i,_ in hits)
        if w.z>zt-0.04: dz=(zt-0.04)-w.z
    return (ds,dz)
for o in ob('WS110_ground_patch_S_of_y-238'): mv(o,fg)
print('FIX175 done',flush=True)

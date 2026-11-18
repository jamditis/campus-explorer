# ws174: UNIFY #79 — Normal Ave W S curb moved N onto the 2023 LiDAR edge (curb face s -11.30 -> -10.30 in the WS163 road frame)
# Evidence (scripts/ws174/prof174.out, edge174.out; prep/ws174_scurb): class-2 intensity is asphalt (<3k) to s -10.25 and concrete/lawn (>7k) from s -10.5
# at every non-driveway station t -65..-2.5 (2023) and t -10..0 (2017 J5D6 tile); median-z rises 10-15 cm across s -10.25..-10.75 (curb). Width 10.3 m.
# Mapping in s (per vertex, t-dependent shift D(t)): road s in [-11.30,-5.65] compressed to [-11.30+D,-5.65]; curb+walk band [-13.08,-11.30] shifted +D;
# lip band [-14.48,-13.08] stretched so its front follows the walk back edge; nothing beyond -14.48 moves. z unchanged (walk/curb keep their profile).
# Taper: D = 1.0 for t <= -12; smooth cosine to 0.19 at t = -0.82 (meets the WS110 curb face s -11.12 at t 1.27). WS110 itself is also ~0.8 m S of the
# LiDAR edge (2017 t 0..20) -> new UNIFY #80; the taper is an interim join (UNVERIFIED) until WS110's S side moves too.
import bpy, math, numpy as np
OB=bpy.data.objects
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def D(t):
    if t<=-12.0: return 1.0
    if t>=-0.82: return 0.19
    u=(t+12.0)/11.18; return 0.19+(1.0-0.19)*0.5*(1+math.cos(math.pi*u))
def f(s,t):
    d=D(t)
    if -11.30<=s<=-5.65: return -5.65+(s+5.65)*(5.65-d)/5.65
    if -13.08-1e-4<=s<-11.30: return s+d
    if -14.48<=s<-13.08: return -14.48+(s+14.48)*(1.40+d)/1.40
    return s
NAMES=['WS163_NormalAve_W_carriageway_LiDAR2023_int_edges_W11p3_UNVERIF','WS163_NormalAve_W_S_curb_UNVERIFIEDsection','WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED',
 'WS163_walk_back_lawn_lip_S_UNVERIFIED','WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5','WS113_paving_tops_proxy',
 'WS173_driveway_D1','WS173_driveway_D2','WS173_driveway_D3']
tot=0
for o in OB:
    if o.type!='MESH' or not any(o.name.startswith(n) for n in NAMES): continue
    mw=o.matrix_world; mi=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co; d=np.array((w.x,w.y))-A; s=float(d@N); t=float(d@T)
        if t<-79.5 or t>-0.80 or s<-14.5 or s>-5.6: continue
        if o.name.startswith('WS163_NormalAve_W_carriageway') and s>-5.66: continue
        s2=f(s,t)
        if abs(s2-s)<1e-6: continue
        p=A+N*s2+T*t; w.x=float(p[0]); w.y=float(p[1]); v.co=mi@w; k+=1
    o.data.update(); tot+=k; print('FIX174',o.name,'moved',k,flush=True)
print('FIX174 total',tot,flush=True)

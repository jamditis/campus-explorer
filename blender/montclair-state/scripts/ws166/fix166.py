# ws166: UNIFY #70 — Lot 3 aisle-mouth bed E edge vs concrete spur.
# Evidence (2023 LiDAR class 2, las163.npy): no curb/step at the bed's E side — ground profile across x -301..-299 at y -250 is flat
# (116.79-116.82 m, noise ~2 cm) and the low-intensity (mulch) zone ends at x ~ -298.7 where bright (lawn, NIR) begins; the ortho concrete
# strip sits in that seam. So the mulch should finish ~2 cm below the spur top along the shared edge (no 0.2 m brown face), easing back to
# the ws165c grade over 0.6 m westwards. Also push any lawn verts that show through the bed (SE corner at walk/spur, W curb fleck).
import bpy, numpy as np, math
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws166/hdr166.py').read())
mu=OB['WS165_aisle_mouth_mulch_bed_graded_to_walk_UNIFY69']; sp=OB['WS165_concrete_spur_N_of_walk_ortho2020_UNVERIFIEDfunction']
TS=bvh([sp]); mw=mu.matrix_world; mi=mw.inverted()
def sz(y):
    for xx in (-299.98,-299.9,-299.8):
        z=hz(TS,xx,y)
        if z is not None: return z
    return None
from collections import defaultdict
G=defaultdict(list)
for v in mu.data.vertices:
    p=mw@v.co; G[(round(p.x,3),round(p.y,3))].append(v)
EW=0.6; mx=0; n=0
for (x,y),vs in G.items():
    if x< XE-EW: continue
    s=sz(y)
    if s is None: continue
    top=max((mw@v.co).z for v in vs); t=min(max((x-(XE-EW))/EW,0),1); t=t*t*(3-2*t)
    tgt=s-0.02
    # never lift above ws165c grade except to meet the spur; front ease near the walk keeps priority (mulch <= walk+0.02 there)
    new=top+(tgt-top)*t
    d=new-top
    if abs(d)>1e-4:
        for v in vs:
            p=mw@v.co; p.z+=d; v.co=mi@p
        n+=1; mx=max(mx,abs(d))
mu.data.update()
print('EDGE166 adjusted xy',n,'max delta',round(mx,3),flush=True)
# ground under the bed (and a 0.15 m margin inside the curb/spur seams) must sit >= 6 cm under the mulch
TM=bvh([mu]); pa=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; gp=OB['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']; pc=0
for g in (pa,gp):
    gw=g.matrix_world; gi=gw.inverted()
    for v in g.data.vertices:
        p=gw@v.co
        if not (XW-0.2<p.x<XE+0.25 and wb(p.x)-0.3<p.y<YN+0.2): continue
        zs=[z for z in (hz(TM,p.x,p.y),hz(TM,min(max(p.x,xi0+0.02),XE-0.02),min(max(p.y,wb(p.x)+0.02),yi1-0.02))) if z is not None]
        if not zs: continue
        zt=min(zs)-0.06
        if p.z>zt: p.z=zt; v.co=gi@p; pc+=1
    g.data.update()
print('GROUND166 pushed',pc,flush=True)
# WS163 lawn lip (thin green strip along the walk back edge) pokes up inside the bed footprint -> the "lawn flecks"; sink it under mulch/spur
lip=OB.get('WS163_walk_back_lawn_lip_N_UNVERIFIED'); TM=bvh([mu]); lc=0
if lip:
    lw=lip.matrix_world; li=lw.inverted()
    for v in lip.data.vertices:
        p=lw@v.co
        if not (XW-0.05<p.x<-298.5): continue
        zs=[z for z in (hz(TM,p.x,p.y),hz(TM,min(max(p.x,xi0+0.02),XE-0.02),max(p.y,wb(p.x)+0.03)),hz(TS,p.x,p.y),hz(TS,min(max(p.x,-299.95),-298.65),max(p.y,wb(p.x)+0.03))) if z is not None]
        if not zs: continue
        zt=min(zs)-0.06
        if p.z>zt: p.z=zt; v.co=li@p; lc+=1
    lip.data.update()
print('LIP166 sunk',lc,flush=True)

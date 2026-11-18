# ws194 WOBBLE SWEEP #W1: Lot 3 S ramp NEAR (E) edge — thin wavy dark lip in the E eye view (ws193 NEXT 1).
# probe194.out: plan line already straight (ws190: x=-305.45+0.0114(y+236), from the 2020 ortho asphalt/vegetation drop),
# but the WS163_ground_patch lawn 0.15 m E of the edge alternates +-1..2 cm above/below the asphalt edge and rises 4-6 cm
# by 0.6 m -> the lawn line laps on and off the asphalt = a wavy dark/light lip. Edge z profile also has small LiDAR ripples.
# Fix (no curb: the ortho shows a plain asphalt-to-grass edge here, no curb shadow): (1) E-edge z profile smoothed along y
# (Gaussian sigma 1.2 m, ends pinned), interior feathered over 0.9 m; (2) lawn E of the edge graded to a clean 2 cm drop below
# the asphalt edge at the line, blending back to the original lawn by 1.0 m; lawn verts under the asphalt clamped 3 cm below it.
# #W2: lawn tongue over the WS193 W curb top (close-up 1844): bank-lawn verts within 0.35 m behind the curb clamped
# 3 cm below the curb top, feathered.
import bpy, bmesh, numpy as np
from mathutils import Vector
def _o(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
D=_o('WS163_Lot3_aisle_S_drive'); M=D.matrix_world; Mi=M.inverted(); me=D.data
W=np.array([tuple(M@v.co) for v in me.vertices])
bm=bmesh.new(); bm.from_mesh(me)
bidx=sorted({v.index for e in bm.edges if e.is_boundary for v in e.verts}); bm.free()
B=np.array(bidx); BW=W[B]
En=lambda y: -305.45+0.0114*(y+236.0)
sel=(np.abs(BW[:,0]-En(BW[:,1]))<0.12)&(BW[:,1]<-235.6)&(BW[:,1]>-250.3)
ei=B[sel]; ei=ei[np.argsort(-W[ei,1])]
ey=W[ei,1]; ez=W[ei,2]
sm=ez.copy()
for k in range(1,len(ei)-1):
    w=np.exp(-0.5*((ey-ey[k])/1.2)**2); sm[k]=(w*ez).sum()/w.sum()
# keep the steepening at the apron (last 2 pts) closer to original
sm[-2:]=0.5*sm[-2:]+0.5*ez[-2:]
dz=sm-ez
print('FIX194 Eedge pts',len(ei),'max|dz| %.3f'%np.abs(dz).max(),flush=True)
def dzat(y): return np.interp(-y,-ey,dz)
def edgez(y): return np.interp(-y,-ey,sm)
N=W.copy(); nf=0
ymin,ymax=ey.min(),ey.max()
for i,(x,y,z) in enumerate(W):
    if not (ymin<=y<=ymax): continue
    d=En(y)-x
    if -0.15<d<0.9:
        t=max(0.0,min(1.0,d/0.9)); f=1-t*t*(3-2*t); N[i,2]=z+f*dzat(y); nf+=1
for v in me.vertices: v.co=Mi@Vector(N[v.index])
me.update(); print('FIX194 drive verts adjusted',nf,flush=True)
# lawn
L=_o('WS163_ground_patch_W_of_WS110'); ML=L.matrix_world; MLi=ML.inverted(); lme=L.data
nl=0; nu=0
for v in lme.vertices:
    p=ML@v.co
    if not (ymin-0.3<=p.y<=ymax+0.1): continue
    d=p.x-En(p.y)
    ez_=edgez(min(max(p.y,ymin),ymax))
    if 0<=d<1.0:
        t=d/1.0; t=t*t*(3-2*t)
        tgt=(1-t)*(ez_-0.02)+t*p.z
        if d<0.5: tgt=min(tgt,ez_-0.025+0.02*d)  # never above the asphalt at the line
        p.z=tgt; v.co=MLi@p; nl+=1
    elif -3.0<d<0 and p.z>ez_-0.03 and p.y>-249.0:
        p.z=ez_-0.03; v.co=MLi@p; nu+=1
lme.update(); print('FIX194 lawn graded',nl,'under-clamped',nu,flush=True)
# W2: lawn behind the WS193 curb
C=_o('WS193_Lot3_S_ramp_W_curb'); MC=C.matrix_world
cv=[MC@v.co for v in C.data.vertices]
tops=np.array([tuple(cv[4*k+1]) for k in range(len(cv)//4)])  # b = top inner
nt=0
for nm in ('WS186_Lot3_S_bank_lawn','WS187_Lot3_W_shoulder_toe','WS162_Lot3_W_shoulder_lawn','WS169c_Lot3_S_end_lawn','WS163_ground_patch_W_of_WS110'):
    try: o=_o(nm)
    except IndexError: continue
    Mo=o.matrix_world; Moi=Mo.inverted(); c=0
    for v in o.data.vertices:
        p=Mo@v.co
        dd=np.hypot(tops[:,0]-p.x,tops[:,1]-p.y); k=int(dd.argmin())
        if dd[k]<0.5 and p.x<tops[k,0]+0.02:
            lim=tops[k,2]-0.03-0.15*max(0.0,dd[k]-0.17)
            if p.z>lim: p.z=lim; v.co=Moi@p; c+=1
    o.data.update(); nt+=c
    if c: print('FIX194 W2',nm,c,flush=True)
print('FIX194 W2 total',nt,flush=True)

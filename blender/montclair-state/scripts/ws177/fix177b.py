# UNIFY #83 (ws177): WS110 Normal Ave NORTH side onto LiDAR curb z-step + 2020 ortho walk band (prep/ws177_ncurb/REFS.md).
# Curb face c(t)=face(t)+o(t) (o smoothed from valid z-step stations), verge narrowed to the ortho dark strip,
# walk (1.5 m) moved onto the ortho bright band; carriageway N edge follows the curb; lawn behind the new walk
# back edge regraded smoothly (exposed strip), ground under the new paving clamped below it.  Window t 54..192.
import bpy, numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
face=lambda t: -0.01462*t+0.292
ST=np.array([(54,0),(56,0),(62,-0.55),(66,-0.95),(78,-1.0),(82,-0.75),(94,-0.95),(110,-0.8),(116,-0.8),(134,-0.75),(138,-0.55),(142,-0.3),(150,0),(154,0.1),(158,0.4),(162,0.6),(176,0.6),(192,0.0)])
OE=np.array([(54,0.25),(60,-0.05),(66,-0.35),(72,-0.65),(78,-0.8),(84,-0.95),(90,-1.1),(114,-1.1),(120,-0.95),(126,-0.8),(132,-0.8),(138,-0.65),(150,-0.65),(156,-0.8),(174,-0.8),(180,-0.95),(192,-0.95)])
tg=np.arange(40,200,0.25)
def gsm(y,sig=3.0):
    k=np.exp(-0.5*(np.arange(-40,41)*0.25/sig)**2); k/=k.sum(); yp=np.pad(y,40,mode='edge'); return np.convolve(yp,k,'valid')
o_g=gsm(np.interp(tg,ST[:,0],ST[:,1]))
c_g=face(tg)+o_g
w_g=np.maximum(gsm(np.interp(tg,OE[:,0],OE[:,1])), c_g+0.3+0.45)   # walk inner edge (>= 0.45 m verge)
w_g=np.minimum(w_g, face(tg)+1.8)                                  # never push the walk further N than now
wt=np.clip(np.minimum((tg-54)/6.0,(192-tg)/6.0),0,1)               # ease in/out of the window
c_g=face(tg)+(c_g-face(tg))*wt; w_g=face(tg)+1.8+(w_g-face(tg)-1.8)*wt
C=lambda t: np.interp(t,tg,c_g); Wn=lambda t: np.interp(t,tg,w_g)
for t in (60,66,78,94,110,134,150,162,180): print('FIX177B t %d face %+.2f curb %+.2f walk %+.2f verge %.2f'%(t,face(t),C(t),Wn(t),Wn(t)-C(t)-0.3))
def verts(o):
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]); W=V@M[:3,:3].T+M[:3,3]
    d=W[:,:2]-A; return M,W, d@T, d@N
def setw(o,M,W,idx):
    Mi=np.linalg.inv(M); L=W[idx]@Mi[:3,:3].T+Mi[:3,3]
    for i,l in zip(idx,L): o.data.vertices[i].co=l
    o.data.update()
def remap_s(t,u):
    c=C(t); w=Wn(t); f=face(t)
    return np.where(u<0.3, c+u, np.where(u<1.8, c+0.3+(u-0.3)/1.5*(w-c-0.3), w+(u-1.8)))
OB=bpy.data.objects
pav=[o for o in OB if o.type=='MESH' and o.name.startswith(('WS110_NormalAve_curb','WS110_NormalAve_verge','WS110_NormalAve_sidewalk','WS110_NormalAve_carriageway','WS113_paving_tops_proxy'))]
back=[]  # (t, z) of the old walk back edge top
for o in pav:
    M,W,t,s=verts(o); u=s-face(t)
    k=(t>40)&(t<200)&(u>-0.25)&(u<3.45)
    if 'carriageway' in o.name: k&=(u<0.1)
    if 'proxy' in o.name: k&=(s>-6)
    if 'sidewalk' in o.name:
        kb=k&(u>3.2); back+=list(zip(t[kb],W[kb,2]))
    idx=np.where(k)[0]; s2=remap_s(t[idx],u[idx]); W[idx,:2]=A+np.outer(t[idx],T)+np.outer(s2,N); setw(o,M,W,idx)
    print('FIX177B paving %s moved %d'%(o.name[:44],len(idx)),flush=True)
B=np.array(back); B=B[np.argsort(B[:,0])]
tb=np.unique(np.round(B[:,0],1)); zb=np.array([B[abs(B[:,0]-x)<0.15,1].max() for x in tb])
ZB=lambda t: np.interp(t,tb,zb)
for o in [x for x in OB if x.type=='MESH' and x.name.startswith(('WS110_ground_patch','WS138b_ground_fill','WS134_ground_patch','WS133b_ground_patch'))]:
    M,W,t,s=verts(o); u=s-face(t); f=face(t)
    k=(t>54)&(t<192)
    nb=Wn(t)+1.5-f                # new walk back edge in u
    under=k&(u>C(t)-f-0.3)&(u<nb)  # under new curb/verge/walk: keep below paving top
    expo=k&(u>=nb)&(u<3.3+1.0)    # exposed strip behind the new walk -> smooth ramp to the old ground 1 m behind the old back edge
    n1=n2=0
    for i in np.where(under)[0]:
        zt=ZB(t[i])-0.04
        if W[i,2]>zt: W[i,2]=zt; n1+=1
    # target ground beyond: sample existing ground z at u≈4.3 per t (median of verts there)
    far=k&(u>4.0)&(u<5.0)
    if far.any():
        tf=t[far]; zf=W[far,2]; order=np.argsort(tf)
        for i in np.where(expo)[0]:
            z_far=np.interp(t[i],tf[order],zf[order]); a=np.clip((u[i]-nb[i])/max(4.3-nb[i],0.3),0,1)
            z_new=ZB(t[i])-0.02+(z_far-(ZB(t[i])-0.02))*a
            if abs(z_new-W[i,2])<1.5: W[i,2]=z_new; n2+=1
    idx=np.where(under|expo)[0]; setw(o,M,W,idx); print('FIX177B ground %s clamped %d regraded %d'%(o.name[:44],n1,n2),flush=True)
print('FIX177B done',flush=True)

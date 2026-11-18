# UNIFY #84: remove the vertical kink at the WS163/WS110 Normal Ave joint (WS110 first ~3 m high).
import bpy, numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
def find(pre):
    c=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(pre)]
    return c[0] if c else None
def verts(o):
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]); W=V@M[:3,:3].T+M[:3,3]
    d=W[:,:2]-A; return W, d@T, d@N
def fit(t,s,z):
    X=np.c_[np.ones_like(t),t,s]; c,*_=np.linalg.lstsq(X,z,rcond=None); return c
T0,T1=-0.82,4.0
pairs=[('WS110_NormalAve_curb_W11p3','WS163_NormalAve_W_S_curb','WS174_junction_bridge_S_curb'),
       ('WS110_NormalAve_sidewalk_ws85','WS163_NormalAve_W_S_sidewalk','WS174_junction_bridge_S_walk'),
       ('WS110_NormalAve_carriageway','WS163_NormalAve_W_carriageway','WS174_junction_bridge_carriageway')]
dzlog=[]
for p110,p163,pbr in pairs:
    o110,o163,obr=find(p110),find(p163),find(pbr)
    if not(o110 and o163 and obr): print('FIX176 missing',p110,o110,o163,obr); continue
    W1,t1,s1=verts(o110); W3,t3,s3=verts(o163)
    m1=(t1>4)&(t1<9); m3=(t3>-5)&(t3<-0.9)
    if pbr.endswith('carriageway'): m1&=(s1>-10)&(s1<0); m3&=(s3>-10)&(s3<0)
    else: m1&=s1<-8; m3&=s3<-8
    c1=fit(t1[m1],s1[m1],W1[m1,2]); c3=fit(t3[m3],s3[m3],W3[m3,2])
    sm=np.median(s1[m1]); P1=lambda t,s: c1[0]+c1[1]*t+c1[2]*s; P3=lambda t,s: c3[0]+c3[1]*t+c3[2]*s
    gap=P1(T0,sm)-P3(T0,sm)
    # measured local excess of WS110 at its start vs its own fit
    ms=(t1<2.5)&(t1>1.0)&(m1|True)
    print('FIX176 %s n110 %d n163 %d slope110 %.4f slope163 %.4f joint_gap_at_T0 %+.3f'%(p110,m1.sum(),m3.sum(),c1[1],c3[1],gap))
    def dz(t,s):
        tgt=P3(T0,s)+(P1(T1,s)-P3(T0,s))*(t-T0)/(T1-T0)
        return np.where(t<T1, tgt-P1(t,s), 0.0)
    # apply to WS110 verts t in [1.0,4)
    k=(t1<T1)&(t1>0.9); d=dz(t1[k],s1[k]); print('FIX176  WS110 verts %d dz %+.3f..%+.3f'%(k.sum(),d.min() if k.any() else 0,d.max() if k.any() else 0))
    if k.any() and abs(d).max()<0.3:
        idx=np.where(k)[0]
        for i,dd in zip(idx,d): o110.data.vertices[i].co.z+=dd
        dzlog.append(np.median(d))
    Wb,tb,sb=verts(obr); d1=dz(np.full_like(tb,1.25),sb); w=np.clip((tb-T0)/(1.25-T0),0,1); db=d1*w
    if abs(db).max()<0.3:
        for i,dd in enumerate(db): obr.data.vertices[i].co.z+=dd
    print('FIX176  bridge %s verts %d dz %+.3f..%+.3f'%(obr.name[:30],len(db),db.min(),db.max()))
    o110.data.update(); obr.data.update()
# ground + proxy under the joint: lower by the walk/road dz (never raise)
if dzlog:
    g=float(min(0.0,np.min(dzlog)))
    for pre in ['WS113_paving_tops_proxy','WS110_ground_patch_S_of_y-238']:
        for o in [x for x in bpy.data.objects if x.type=='MESH' and x.name.startswith(pre)]:
            W,t,s=verts(o); k=(t>T0)&(t<T1)&(s>-13.5)&(s<1.0)
            w=np.where(t<1.25,np.clip((t-T0)/(1.25-T0),0,1),np.clip((T1-t)/(T1-1.25),0,1))
            n=0
            for i in np.where(k)[0]: o.data.vertices[i].co.z+=g*w[i]; n+=1
            o.data.update(); print('FIX176 ground %s lowered %d by up to %+.3f'%(o.name[:30],n,g))
print('FIX176 done')

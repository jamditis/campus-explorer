# UNIFY #84 (ws177): remove the grade break at the WS163/WS110 Normal Ave joint.
# Current longitudinal profile (curb top, identical N and S; whole cross-section follows it):
# WS163 slope eases 0.040 -> 0.023 /m toward t -0.82, bridge jumps 0.070 /m, WS110 0.030 /m.
# Target: one cubic Hermite grade t -4.42 -> 5.37 matching z and slope at both ends (0.040 -> 0.032 /m).
# dz(t) = H(t) - P(t) is applied to EVERY road vertex at that t (curbs, walks, carriageway, bridges, verge,
# paving proxy) so cross-sections and the curb reveal are preserved exactly; lawn lips follow with falloff,
# ground under/behind paving is only ever lowered.  |dz| <= 0.036 m.
import bpy, numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
P=np.array([(-5.96,117.393),(-5.45,117.415),(-4.93,117.436),(-4.42,117.456),(-3.90,117.477),(-3.39,117.496),(-2.88,117.515),(-2.36,117.529),(-1.85,117.544),(-1.34,117.556),(-0.82,117.568),(1.27,117.715),(3.32,117.775),(5.37,117.841),(7.60,117.913),(9.83,118.001)])
t0,z0,m0,t1,z1,m1=-4.42,117.456,0.0398,5.37,117.841,0.0323
def H(t):
    h=t1-t0; u=(t-t0)/h
    return (2*u**3-3*u**2+1)*z0+(u**3-2*u**2+u)*h*m0+(-2*u**3+3*u**2)*z1+(u**3-u**2)*h*m1
def DZ(t):
    t=np.asarray(t,float); d=H(t)-np.interp(t,P[:,0],P[:,1]); return np.where((t>t0)&(t<t1),d,0.0)
def verts(o):
    M=np.array(o.matrix_world); V=np.array([v.co[:] for v in o.data.vertices]); W=V@M[:3,:3].T+M[:3,3]
    d=W[:,:2]-A; return W, d@T, d@N
def apply(o,dz):
    if o.matrix_world.to_3x3().determinant()<=0: print('FIX177 skip (bad matrix)',o.name); return 0
    sz=o.matrix_world.to_scale().z; n=0
    for i in np.where(abs(dz)>1e-5)[0]: o.data.vertices[i].co.z+=dz[i]/sz; n+=1
    o.data.update(); return n
road=('WS163_NormalAve_W_','WS110_NormalAve_','WS174_junction_bridge_')
for o in [x for x in bpy.data.objects if x.type=='MESH' and x.name.startswith(road)]:
    W,t,s=verts(o); d=DZ(t); n=apply(o,d)
    if n: print('FIX177 road %s %d dz %+.3f..%+.3f'%(o.name[:44],n,d.min(),d.max()),flush=True)
for o in [x for x in bpy.data.objects if x.type=='MESH' and x.name.startswith('WS113_paving_tops_proxy')]:
    W,t,s=verts(o); d=DZ(t)*((s>-12.45)&(s<3.65)); print('FIX177 proxy',apply(o,d))
for o in [x for x in bpy.data.objects if x.type=='MESH' and 'lip' in x.name.lower() and x.name.startswith(('WS163_','WS175_','WS174_','WS176_'))]:
    W,t,s=verts(o); w=np.where(s<0,np.clip((s+13.9)/1.7,0,1),np.clip((5.2-s)/1.7,0,1)); d=DZ(t)*w
    print('FIX177 lip %s %d'%(o.name[:44],apply(o,d)))
for o in [x for x in bpy.data.objects if x.type=='MESH' and x.name.startswith(('WS110_ground_patch','WS163_ground','WS138b_ground_fill'))]:
    W,t,s=verts(o); w=np.where(s<-12.3,np.clip((s+13.9)/1.6,0,1),np.where(s>3.5,np.clip((5.0-s)/1.5,0,1),1.0)); d=np.minimum(DZ(t),0)*w
    print('FIX177 ground %s %d'%(o.name[:44],apply(o,d)))
print('FIX177 done',flush=True)

# sa pass 2: inside the sa box, snap SA_ground_lower_patch to the unsmoothed north 1 m LiDAR (L-0.03), up AND down, feathered 6 m from the box edge,
# 0 within 3 m of Richardson; shift the same ground-dressing verts (+ RZ2 patch, QW ramp) by the same interpolated delta. Fixes the gauss-smoothed
# Annex lower-walk trench (patch was up to 0.5 m over MK walk) and the 3DEP plaza 1 m low at y 258-272. REVERT=1 restores data/sa/lower2_backup.npz.
import bpy, os, json, numpy as np
REV=os.environ.get('REVERT')=='1'; BK='data/sa/lower2_backup.npz'
def save():
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
def restore():
    if not os.path.exists(BK): return
    d=np.load(BK); n=0
    for k in d.files:
        ob=bpy.data.objects.get(k)
        if ob and len(ob.data.vertices)*3==d[k].size: ob.data.vertices.foreach_set('co',d[k]); ob.data.update(); n+=1
    print('SA2 restored',n)
if REV: restore(); save(); raise SystemExit
if os.path.exists(BK): restore()
X0,X1,Y0,Y1=-110,30,252,310
rich=np.array(json.load(open('data/qp/rich_poly.json'))['outer'])
def pdist(px,py,poly):
    px=np.asarray(px,float); py=np.asarray(py,float); b=np.full(px.shape,1e9); ins=np.zeros(px.shape,bool); n=len(poly)
    for i in range(n):
        ax,ay=poly[i]; bx,by=poly[(i+1)%n]; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1e-9
        t=np.clip(((px-ax)*dx+(py-ay)*dy)/L2,0,1); b=np.minimum(b,np.hypot(px-ax-t*dx,py-ay-t*dy))
        c=((ay>py)!=(by>py))&(px<(bx-ax)*(py-ay)/(by-ay+1e-12)+ax); ins^=c
    return np.where(ins,0,b)
def ss(t): t=np.clip(t,0,1); return t*t*(3-2*t)
Lg=np.load('north/data/grid_1m.npz')['dtm_filled']
P=bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']; M=np.array(P.matrix_world)
me=P.data; n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co); w=co.reshape(-1,3)@M[:3,:3].T+M[:3,3]
xs=np.arange(X0-1,X1+2); ys=np.arange(Y0-1,Y1+2); Pz=np.full((len(ys),len(xs)),np.nan)
ii=np.rint(w[:,0]-xs[0]).astype(int); jj=np.rint(w[:,1]-ys[0]).astype(int); Pz[jj,ii]=w[:,2]
LL=Lg[(ys+260).astype(int)][:,(xs+600).astype(int)].astype(float)
XX,YY=np.meshgrid(xs,ys); edge=np.minimum.reduce([XX-X0,X1-XX,YY-Y0,Y1-YY])
W=ss(edge/6.0)*ss((pdist(XX,YY,rich)-3)/5)*ss((-20.0-XX)/6.0)  # Annex/SW zone only (x<=-26 full, 0 from x -20: the SE court zone keeps the smoothed sa pass)
E=np.nan_to_num((LL-0.03-Pz)*W,nan=0.0)
np.savez('data/sa/field2.npz',xs=xs,ys=ys,Pz=Pz,L=LL,W=W,E=E)
print('SA2 E min %.2f max %.2f |E|>0.1: %d'%(E.min(),E.max(),int((abs(E)>0.1).sum())))
def Eat(x,y):
    fx=np.clip(x-xs[0],0,len(xs)-1.001); fy=np.clip(y-ys[0],0,len(ys)-1.001); i=np.floor(fx).astype(int); j=np.floor(fy).astype(int); tx=fx-i; ty=fy-j
    v=E[j,i]*(1-tx)*(1-ty)+E[j,i+1]*tx*(1-ty)+E[j+1,i]*(1-tx)*ty+E[j+1,i+1]*tx*ty
    return np.where((x<X0)|(x>X1)|(y<Y0)|(y>Y1),0,v)
COLS=['QX_StudentCenter_plaza_paving_UNVERIFIED','QY_plaza_rim_band_UNVERIFIED','QY_walk_junction_wear_UNVERIFIED','QS_Richardson_walks_UNVERIFIED',
 'QT_Richardson_walk_soil_edge_UNVERIFIED','QW_Richardson_walk_ext_UNVERIFIED','QS_Richardson_lawn_grass_20261102qs','QV_Richardson_NW_lawn_grass_20261103qv','QX_Richardson_W_ramp_grass_20261103qx']
objs={P,bpy.data.objects['QW_DTM_north_edge_ramp_UNVERIFIED'],bpy.data.objects['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']}
for cn in COLS:
    c=bpy.data.collections.get(cn)
    if c: objs|={o for o in c.all_objects if o.type=='MESH' and 'plinth' not in o.name}
bk={}; st={}
for o in objs:
    m_=o.data; k=len(m_.vertices); c0=np.zeros(k*3); m_.vertices.foreach_get('co',c0)
    Mo=np.array(o.matrix_world); wv=c0.reshape(-1,3)@Mo[:3,:3].T+Mo[:3,3]; d=Eat(wv[:,0],wv[:,1]); m=abs(d)>0.002
    if not m.any(): continue
    wv[m,2]+=d[m]; Mi=np.linalg.inv(Mo); nl=wv@Mi[:3,:3].T+Mi[:3,3]
    bk[o.name]=c0.copy(); m_.vertices.foreach_set('co',nl.ravel()); m_.update(); st[o.name[:36]]=(int(m.sum()),round(float(d.min()),2),round(float(d.max()),2))
np.savez(BK,**bk); print('SA2 shifted',st); save()

# rz2 (Nov 4 2026, MAIN). ALL UNVERIFIED, reversible: REVERT=1 removes RZ2 patch + restores lifted verts exactly from data/rz2/lift_backup.npz.
# Problem (rz finding): MAIN ground round the Student Center = coarse 3DEP skirt (+QW ramp), 1.2-1.7 m BELOW the north 1 m LiDAR
# on the court's east side, so the north court slab (top 140.78) stood ~1.5 m proud of the QXP plaza.
# Fix: D(x,y)=max(0, LiDAR dtm_filled - current ground) (gaussian-smoothed 2 m), weight 1 within 10 m of OSM 313026743, feathered to 0
# by 26 m, 0 within 2 m of Richardson (ramps in over 5 m). New 1 m patch RZ2_SC_LiDAR_ground_patch at ground+D-0.05 (skirt material),
# and QXP/QY/wear/grass/walk verts lifted by D. LIFT ONLY: where LiDAR is LOWER than MAIN (SW/SE corners) nothing is lowered.
import bpy, bmesh, os, math, json, numpy as np
from mathutils import Vector, interpolate
REV=os.environ.get('REVERT')=='1'; NAME='RZ2_SC_LiDAR_ground_patch_UNVERIFIED'; BK='data/rz2/lift_backup.npz'
def restore():
    o=bpy.data.objects.get(NAME)
    if o: me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
    n=0
    if os.path.exists(BK):
        d=np.load(BK)
        for k in d.files:
            ob=bpy.data.objects.get(k)
            if ob and len(ob.data.vertices)*3==d[k].size: ob.data.vertices.foreach_set('co',d[k]); ob.data.update(); n+=1
    print('RZ2 restored',n)
def save():
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if REV: restore(); save(); raise SystemExit
if bpy.data.objects.get(NAME) or os.path.exists(BK): restore()
X0,X1,Y0,Y1=-80,62,248,372
fp=np.array(json.load(open('data/qr/day8_prep/student_center_footprints_local_qr.json'))['ways']['313026743']['pts_local_m'])[:-1]
rich=np.array(json.load(open('data/qp/rich_poly.json'))['outer'])
def pdist(px,py,poly):
    # vectorised distance to polygon (0 inside)
    px=np.asarray(px,float); py=np.asarray(py,float); b=np.full(px.shape,1e9); ins=np.zeros(px.shape,bool); n=len(poly)
    for i in range(n):
        ax,ay=poly[i]; bx,by=poly[(i+1)%n]; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1e-9
        t=np.clip(((px-ax)*dx+(py-ay)*dy)/L2,0,1); b=np.minimum(b,np.hypot(px-ax-t*dx,py-ay-t*dy))
        c=((ay>py)!=(by>py))&(px<(bx-ax)*(py-ay)/(by-ay+1e-12)+ax); ins^=c
    return np.where(ins,0,b)
def ss(t): t=np.clip(t,0,1); return t*t*(3-2*t)
L=np.load('north/data/grid_1m.npz')['dtm_filled']
dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; rp=bpy.data.objects['QW_DTM_north_edge_ramp_UNVERIFIED']
ske=sk.evaluated_get(dg); rpe=rp.evaluated_get(dg)
def rc(o,e,x,y):
    iw=o.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
    return ((o.matrix_world@r[1]).z,r[3],r[1]) if r[0] else None
xs=np.arange(X0,X1+1); ys=np.arange(Y0,Y1+1); G=np.full((len(ys),len(xs)),np.nan); A={}
skd=ske.data; attrs=[a for a in ('ou_edge','ow2_strip') if a in skd.attributes]
for a in attrs: A[a]=np.zeros(G.shape)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        h=rc(sk,ske,float(x),float(y)); z=h[0] if h else np.nan
        if h:
            p=skd.polygons[h[1]]; vs=[skd.vertices[k].co for k in p.vertices]; w=interpolate.poly_3d_calc(vs,h[2])
            for a in attrs: A[a][j,i]=sum(wi*skd.attributes[a].data[k].value for wi,k in zip(w,p.vertices))
        h2=rc(rp,rpe,float(x),float(y))
        if h2 and (np.isnan(z) or h2[0]>z): z=h2[0]
        G[j,i]=z
LL=L[(ys+260).astype(int)][:,(xs+600).astype(int)].astype(float)
D0=np.nan_to_num(LL-G,nan=0.0)
def gs(a,s=2.0):
    k=np.exp(-0.5*(np.arange(-6,7)/s)**2); k/=k.sum(); p=np.pad(a,6,mode='edge')
    p=np.apply_along_axis(lambda r:np.convolve(r,k,'same'),1,p); p=np.apply_along_axis(lambda r:np.convolve(r,k,'same'),0,p); return p[6:-6,6:-6]
D0=gs(D0)
XX,YY=np.meshgrid(xs,ys)
W=ss(1-(pdist(XX,YY,fp)-10)/16)*ss((pdist(XX,YY,rich)-2)/5)
D=np.maximum(D0,0)*W; D[np.isnan(G)]=0
np.savez('data/rz2/field.npz',xs=xs,ys=ys,G=G,L=LL,D0=D0,W=W,D=D)
print('RZ2 D max',round(D.max(),2),'cells>0.05',int((D>0.05).sum()),'neg D0 (LiDAR lower) min',round(np.nanmin(D0*W),2))
def Dat(x,y):
    fx=np.clip(x-X0,0,len(xs)-1.001); fy=np.clip(y-Y0,0,len(ys)-1.001); i=np.floor(fx).astype(int); j=np.floor(fy).astype(int); tx=fx-i; ty=fy-j
    v=D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty
    return np.where((x<X0)|(x>X1)|(y<Y0)|(y>Y1),0,v)
# ---- patch
iw=sk.matrix_world.inverted(); bm=bmesh.new(); grid={}
for j in range(len(ys)):
    for i in range(len(xs)):
        if np.isnan(G[j,i]): continue
        grid[i,j]=bm.verts.new(iw@Vector((float(xs[i]),float(ys[j]),float(G[j,i]+D[j,i]-0.05))))
nf=0
for j in range(len(ys)-1):
    for i in range(len(xs)-1):
        q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if not all(k in grid for k in q) or max(D[k[1],k[0]] for k in q)<0.05: continue
        bm.faces.new([grid[k] for k in q]); nf+=1
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for f in bm.faces:
    if (sk.matrix_world.to_3x3()@f.normal).z<0: f.normal_flip()
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
mw=sk.matrix_world; wc=np.array([tuple(mw@v.co) for v in me.vertices])
ii=np.rint(wc[:,0]-X0).astype(int); jj=np.rint(wc[:,1]-Y0).astype(int)
for a in attrs:
    at=me.attributes.new(a,'FLOAT','POINT'); at.data.foreach_set('value',A[a][jj,ii].astype(np.float32))
uv=me.uv_layers.new(name='ortho')
for p in me.polygons:
    for li in p.loop_indices:
        w=wc[me.loops[li].vertex_index]; uv.data[li].uv=(0.00025*w[0]+0.5,0.00025*w[1]+0.5)
me.materials.append(sk.material_slots[0].material)
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new(NAME,me); ob.matrix_world=mw.copy(); sk.users_collection[0].objects.link(ob)
ob['UNVERIFIED_rz2']='ground lifted to north 1 m LiDAR dtm_filled round the Student Center (lift only, 2 m gauss, 10->26 m feather)'
print('RZ2 patch faces',nf,'verts',len(me.vertices))
# ---- lift
COLS=['QX_StudentCenter_plaza_paving_UNVERIFIED','QY_plaza_rim_band_UNVERIFIED','QY_walk_junction_wear_UNVERIFIED','QS_Richardson_walks_UNVERIFIED',
 'QT_Richardson_walk_soil_edge_UNVERIFIED','QW_Richardson_walk_ext_UNVERIFIED','QS_Richardson_lawn_grass_20261102qs','QV_Richardson_NW_lawn_grass_20261103qv','QX_Richardson_W_ramp_grass_20261103qx']
bk={}; st={}
for cn in COLS:
    c=bpy.data.collections.get(cn)
    if not c: print('missing',cn); continue
    for o in c.all_objects:
        if o.type!='MESH' or o.name in bk or 'plinth' in o.name: continue
        me=o.data; n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co)
        M=np.array(o.matrix_world); w=co.reshape(-1,3)@M[:3,:3].T+M[:3,3]; d=Dat(w[:,0],w[:,1])
        m=d>0.002
        if not m.any(): continue
        w[m,2]+=d[m]; Mi=np.linalg.inv(M); nl=w@Mi[:3,:3].T+Mi[:3,3]
        bk[o.name]=co.copy(); me.vertices.foreach_set('co',nl.ravel()); me.update(); st[o.name[:40]]=(int(m.sum()),round(float(d.max()),2))
np.savez(BK,**bk); print('RZ2 lifted',st); save()

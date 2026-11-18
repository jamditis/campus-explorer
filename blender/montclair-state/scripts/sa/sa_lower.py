# sa (Nov 4 2026, MAIN). ALL UNVERIFIED, reversible (REVERT=1): lower MAIN ground to the north 1 m LiDAR where the 3DEP skirt/QW ramp
# stands ABOVE it round the Student Center SW/SE corners + the Annex deck/low-wall strip (rz2 was lift-only).
# Skirt base mesh is bisected on the box X0..X1/Y0..Y1 and the faces inside deleted (original mesh kept as fake-user SA_skirt_mesh_backup);
# a 1 m patch SA_ground_lower_patch fills the hole at T+Dneg-0.03 (T = current top: skirt/ramp + rz2 lift), with a 1 m apron under the skirt.
# Dneg = min(0, gauss2m(L - T)) * W (W 0 at the box edge -> 1 at 6 m in, 0 within 3 m of Richardson). Ground dressing verts lowered by Dneg
# (backup data/sa/lower_backup.npz); trees/instances in the box moved by Dneg at their origin (data/sa/lower_obj.json).
import bpy, bmesh, os, json, numpy as np
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; NAME='SA_ground_lower_patch_UNVERIFIED'; BK='data/sa/lower_backup.npz'; BJ='data/sa/lower_obj.json'
SK='Context_skirt_3DEP_ortho_4km'; SKB='SA_skirt_mesh_backup'
X0,X1,Y0,Y1=-110,30,252,310
def restore():
    o=bpy.data.objects.get(NAME)
    if o: me=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(me)
    sk=bpy.data.objects[SK]; b=bpy.data.meshes.get(SKB)
    if b: cur=sk.data; sk.data=b; b.use_fake_user=False; b.name=cur.name+'_tmp'; nm=cur.name; bpy.data.meshes.remove(cur); b.name=nm
    n=0
    if os.path.exists(BK):
        d=np.load(BK)
        for k in d.files:
            ob=bpy.data.objects.get(k)
            if ob and len(ob.data.vertices)*3==d[k].size: ob.data.vertices.foreach_set('co',d[k]); ob.data.update(); n+=1
    if os.path.exists(BJ):
        for k,z in json.load(open(BJ)).items():
            ob=bpy.data.objects.get(k)
            if ob: ob.location.z=z
    print('SA_LOWER restored',n)
def save():
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if REV: restore(); save(); raise SystemExit
if bpy.data.objects.get(NAME) or bpy.data.meshes.get(SKB): restore()
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
dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects[SK]; rp=bpy.data.objects['QW_DTM_north_edge_ramp_UNVERIFIED']; ske=sk.evaluated_get(dg); rpe=rp.evaluated_get(dg)
def rc(o,e,x,y):
    iw=o.matrix_world.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
    return (o.matrix_world@r[1]).z if r[0] else np.nan
A=1  # apron
xs=np.arange(X0-A,X1+A+1); ys=np.arange(Y0-A,Y1+A+1); G=np.full((len(ys),len(xs)),np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        z=rc(sk,ske,float(x),float(y)); z2=rc(rp,rpe,float(x),float(y))
        if not np.isnan(z2) and (np.isnan(z) or z2>z): z=z2
        G[j,i]=z
f=np.load('data/rz2/field.npz'); D2=np.zeros_like(G)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        jj=int(y-f['ys'][0]); ii=int(x-f['xs'][0])
        if 0<=jj<len(f['ys']) and 0<=ii<len(f['xs']): D2[j,i]=f['D'][jj,ii]
T=G+D2
LL=Lg[(ys+260).astype(int)][:,(xs+600).astype(int)].astype(float)
def gs(a,s=2.0):
    k=np.exp(-0.5*(np.arange(-6,7)/s)**2); k/=k.sum(); p=np.pad(a,6,mode='edge')
    p=np.apply_along_axis(lambda r:np.convolve(r,k,'same'),1,p); p=np.apply_along_axis(lambda r:np.convolve(r,k,'same'),0,p); return p[6:-6,6:-6]
R=gs(np.nan_to_num(LL-T,nan=0.0))
XX,YY=np.meshgrid(xs,ys)
edge=np.minimum.reduce([XX-X0,X1-XX,YY-Y0,Y1-YY])
W=ss(edge/6.0)*ss((pdist(XX,YY,rich)-3)/5)
Dn=np.minimum(R,0)*W; Dn[np.isnan(G)]=0
np.savez('data/sa/field.npz',xs=xs,ys=ys,G=G,T=T,L=LL,R=R,W=W,Dn=Dn)
print('SA Dn min',round(Dn.min(),2),'cells<-0.05',int((Dn<-0.05).sum()),'nanG',int(np.isnan(G).sum()))
def Dat(x,y):
    fx=np.clip(x-xs[0],0,len(xs)-1.001); fy=np.clip(y-ys[0],0,len(ys)-1.001); i=np.floor(fx).astype(int); j=np.floor(fy).astype(int); tx=fx-i; ty=fy-j
    v=Dn[j,i]*(1-tx)*(1-ty)+Dn[j,i+1]*tx*(1-ty)+Dn[j+1,i]*(1-tx)*ty+Dn[j+1,i+1]*tx*ty
    return np.where((x<X0)|(x>X1)|(y<Y0)|(y>Y1),0,v)
# ---- skirt: bisect + delete inside (base mesh), keep backup
b=sk.data.copy(); b.name=SKB; b.use_fake_user=True
mw=sk.matrix_world; iw=mw.inverted()
bm=bmesh.new(); bm.from_mesh(sk.data)
for (co,no) in [((X0,0,0),(1,0,0)),((X1,0,0),(1,0,0)),((0,Y0,0),(0,1,0)),((0,Y1,0),(0,1,0))]:
    pco=iw@Vector(co); pno=(mw.to_3x3().transposed()@Vector(no)).normalized()
    bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=pco,plane_no=pno,dist=1e-4)
dl=[]
for fc in bm.faces:
    c=mw@fc.calc_center_median()
    if X0<c.x<X1 and Y0<c.y<Y1: dl.append(fc)
bmesh.ops.delete(bm,geom=dl,context='FACES_ONLY'); bm.to_mesh(sk.data); bm.free(); sk.data.update()
print('SA skirt faces deleted',len(dl),'now',len(sk.data.polygons))
# ---- patch
bm=bmesh.new(); grid={}
for j in range(len(ys)):
    for i in range(len(xs)):
        if np.isnan(T[j,i]): continue
        grid[i,j]=bm.verts.new(iw@Vector((float(xs[i]),float(ys[j]),float(T[j,i]+Dn[j,i]-0.03))))
for j in range(len(ys)-1):
    for i in range(len(xs)-1):
        q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if all(k in grid for k in q): bm.faces.new([grid[k] for k in q])
for fc in bm.faces:
    if (mw.to_3x3()@fc.normal).z<0: fc.normal_flip()
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
wc=np.array([tuple(mw@v.co) for v in me.vertices])
uv=me.uv_layers.new(name='ortho')
for p in me.polygons:
    for li in p.loop_indices:
        w=wc[me.loops[li].vertex_index]; uv.data[li].uv=(0.00025*w[0]+0.5,0.00025*w[1]+0.5)
# copy skirt attributes used by its shader (nearest from the backup mesh, evaluated-free: sample rz2 patch/skirt attr names)
for a in ('ou_edge','ow2_strip'):
    if a in b.attributes:
        at=me.attributes.new(a,'FLOAT','POINT'); at.data.foreach_set('value',np.zeros(len(me.vertices),np.float32))
for m in sk.data.materials: me.materials.append(m)
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new(NAME,me); ob.matrix_world=mw.copy(); sk.users_collection[0].objects.link(ob)
ob['UNVERIFIED_sa']='ground lowered to north 1 m LiDAR dtm_filled (lower only) in box x -110..30 y 252..310, replaces bisected skirt faces'
print('SA patch faces',len(me.polygons))
# ---- lower dressing verts
COLS=['QX_StudentCenter_plaza_paving_UNVERIFIED','QY_plaza_rim_band_UNVERIFIED','QY_walk_junction_wear_UNVERIFIED','QS_Richardson_walks_UNVERIFIED',
 'QT_Richardson_walk_soil_edge_UNVERIFIED','QW_Richardson_walk_ext_UNVERIFIED','QS_Richardson_lawn_grass_20261102qs','QV_Richardson_NW_lawn_grass_20261103qv','QX_Richardson_W_ramp_grass_20261103qx']
objs=set()
for cn in COLS:
    c=bpy.data.collections.get(cn)
    if c: objs|={o for o in c.all_objects if o.type=='MESH' and 'plinth' not in o.name}
    else: print('missing',cn)
objs|={rp,bpy.data.objects['RZ2_SC_LiDAR_ground_patch_UNVERIFIED']}
bk={}; st={}
for o in objs:
    me=o.data; n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co)
    M=np.array(o.matrix_world); w=co.reshape(-1,3)@M[:3,:3].T+M[:3,3]; d=Dat(w[:,0],w[:,1]); m=d<-0.002
    if not m.any(): continue
    w[m,2]+=d[m]; Mi=np.linalg.inv(M); nl=w@Mi[:3,:3].T+Mi[:3,3]
    bk[o.name]=co.copy(); me.vertices.foreach_set('co',nl.ravel()); me.update(); st[o.name[:40]]=(int(m.sum()),round(float(d.min()),2))
np.savez(BK,**bk); print('SA lowered',st)
oz={}
for o in bpy.data.objects:
    if o.parent or o.name in bk or o==ob or o.hide_render: continue
    if not (o.name.startswith('T_') or o.type=='EMPTY' and o.instance_collection): continue
    p=o.matrix_world.translation; d=float(Dat(np.array([p.x]),np.array([p.y]))[0])
    if d<-0.02: oz[o.name]=o.location.z; o.location.z+=d
json.dump(oz,open(BJ,'w')); print('SA objs moved',len(oz),list(oz)[:10]); save()

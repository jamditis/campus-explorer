# ws102: full-width College Ave S of the WS27 end (s 0..88 along OSM 1557427669) -- layered build
import bpy, bmesh, numpy as np, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B='/workspace/nj-scenes/montclair-state/scripts/ws102/'
P=np.array(json.load(open(B+'osm102.json'))['1557427669']['p'])[::-1]; seg=np.diff(P,axis=0); L=np.hypot(*seg.T); C=np.r_[0,np.cumsum(L)]
# smooth the polyline direction (avoid kinks): sample centreline every 0.5 m then gaussian smooth
def raw(s):
    k=max(min(np.searchsorted(C,s)-1,len(L)-1),0); return P[k]+(s-C[k])*seg[k]/L[k]
S0,S1=0.0,88.5
ss=np.arange(-6,S1+6.01,0.5); cl=np.array([raw(s) for s in ss])
from math import exp
w=np.array([exp(-0.5*(i*0.5/2.0)**2) for i in range(-8,9)]); w/=w.sum()
cs=np.stack([np.convolve(np.pad(cl[:,i],8,mode='edge'),w,'valid') for i in range(2)],1)
def frame(s):
    i=np.interp(s,ss,np.arange(len(ss))); a=int(min(i,len(ss)-2)); t=i-a
    p=cs[a]*(1-t)+cs[a+1]*t; d=cs[min(a+1,len(ss)-1)]-cs[max(a-1,0)]; d=d/np.linalg.norm(d); n=np.array([d[1],-d[0]]); return p,n
lz=np.load(B+'lid_so.npz'); LS,LO,LZ=lz['s'],lz['o'],lz['z']
def Lc(s):
    q=(abs(LS-s)<1.5)&(abs(LO)<2.5); return np.median(LZ[q]) if q.sum()>5 else np.nan
srow=np.arange(-3,S1+3.1,1.0); lc=np.array([Lc(s) for s in srow]); ok=np.isfinite(lc); lc=np.interp(srow,srow[ok],lc[ok])
lcs=np.convolve(np.pad(lc,3,mode='edge'),np.ones(7)/7,'valid')
cw=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; cco=np.array([cw.matrix_world@v.co for v in cw.data.vertices])
endz=float(np.median(cco[cco[:,1]<-160.3][:,2]))
sp=bpy.data.objects['UA_CollegeAve_spur_1557427669_UNVERIFIED']; sco=np.array([sp.matrix_world@v.co for v in sp.data.vertices])
pe,_=frame(S1); dd=np.hypot(sco[:,0]-pe[0],sco[:,1]-pe[1]); near=dd<max(4.0,np.sort(dd)[6]+0.01); spz=float(np.max(sco[near][:,2])); print('A102 spur near end n',int(near.sum()),'mind %.2f'%dd.min())
def zc(s):
    z=np.interp(s,srow,lcs)+0.04
    t=np.clip(s/4.0,0,1); t=t*t*(3-2*t); z=endz*(1-t)+z*t
    if spz is not None:
        u=np.clip((s-(S1-3))/3.0,0,1); u=u*u*(3-2*u); z=z*(1-u)+(spz+0.005)*u
    return z
def sm(a,b,x):
    t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def eE(s):  # east edge offset (negative = east)
    return -3.45 + (-6.5+3.45)*(sm(0,1.5,s)*(1-sm(21,24.5,s)))
EW=3.3
BANDS=[(0,0.45),(5.55,6.45),(11.55,12.45),(17.55,18.45),(23.05,23.95)]
rows=sorted(set(list(np.round(np.arange(S0,S1+0.01,0.5),3))+[b for ab in BANDS for b in ab]+[S1]))
NC=12
def cols(s):
    e=eE(s); plaza=e<-4.0
    u=[e,e+1.0]+list(np.linspace(e+1.0,2.6,NC)[1:])+[EW]
    return np.array(u)
mats={n:bpy.data.materials[n] for n in ('WS27_CollegeAve_asphalt_2020ortho','WS27_brick_crosswalk_2020ortho','WS27_curb_concrete_UNVERIFIED')}
bm=bmesh.new(); grid=[]
for s in rows:
    p,n=frame(s); z=zc(s); r=[]
    for o in cols(s): q=p+n*o; r.append(bm.verts.new((q[0],q[1],z)))
    grid.append(r)
inplaza=lambda s: s<23.95
for i in range(len(rows)-1):
    sc=0.5*(rows[i]+rows[i+1])
    for j in range(len(grid[i])-1):
        f=bm.faces.new((grid[i][j],grid[i][j+1],grid[i+1][j+1],grid[i+1][j]))
        band=any(a<=sc<=b for a,b in BANDS) or (inplaza(sc) and eE(sc)<-5.0 and (j==0 or j==len(grid[i])-2))
        f.material_index=1 if band else 0
# skirt on long edges
for side in (0,-1):
    for i in range(len(rows)-1):
        a,b=grid[i][side],grid[i+1][side]
        a2=bm.verts.new(a.co-Vector((0,0,0.35))); b2=bm.verts.new(b.co-Vector((0,0,0.35)))
        f=bm.faces.new((a,b,b2,a2)) if side==-1 else bm.faces.new((b,a,a2,b2)); f.material_index=0
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<-0.5: f.normal_flip()
me=bpy.data.meshes.new('WS102_CollegeAve_S_carriageway'); bm.to_mesh(me); bm.free()
for m in ('WS27_CollegeAve_asphalt_2020ortho','WS27_brick_crosswalk_2020ortho'): me.materials.append(mats[m])
ob=bpy.data.objects.new('WS102_CollegeAve_S_carriageway_brickband_table_ortho2020_LiDAR_UNVERIFIED',me)
coll=cw.users_collection[0]; coll.objects.link(ob)
for p_ in me.polygons: p_.use_smooth=False
# curbs (s 21..S1-0.5), 0.15 wide, top = road + reveal
def curb(side):
    bm=bmesh.new(); prev=None
    for s in np.arange(21.0,S1-0.49,0.5):
        p,n=frame(s); z=zc(s); rv=0.15*sm(21,24.5,s)
        if side=='W': o0,o1=EW,EW+0.15
        else: o0,o1=eE(s)-0.15,eE(s)
        a=p+n*o0; b=p+n*o1
        ring=[bm.verts.new((a[0],a[1],z-0.12)),bm.verts.new((a[0],a[1],z+rv)),bm.verts.new((b[0],b[1],z+rv)),bm.verts.new((b[0],b[1],z-0.25))]
        if prev:
            for k in range(3): bm.faces.new((prev[k],prev[k+1],ring[k+1],ring[k]))
        else: bm.faces.new(ring[::-1])
        prev=ring
    bm.faces.new(prev)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new('WS102_curb_'+side); bm.to_mesh(me); bm.free(); me.materials.append(mats['WS27_curb_concrete_UNVERIFIED'])
    o=bpy.data.objects.new('WS102_CollegeAve_S_curb_%s_LiDARstep12-20cm_UNVERIFIED'%side,me); coll.objects.link(o); return o
cW=curb('W'); cE=curb('E')
# retire spur faces under the new road
bm=bmesh.new(); bm.from_mesh(sp.data); bm.faces.ensure_lookup_table(); mw=sp.matrix_world
roadpoly=[]
for s in np.arange(-0.5,S1-0.4,0.5):
    p,n=frame(s); roadpoly.append((s,p,n))
def inside(x,y):
    for s,p,n in roadpoly[::2]:
        d=np.array([x,y])-p; o=d@n; t=d@np.array([-n[1],n[0]])
        if abs(t)<0.6 and eE(s)-0.2<=o<=EW+0.2: return True
    return False
dl=[f for f in bm.faces if inside(*(mw@f.calc_center_median())[:2])]
bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(sp.data); bm.free(); print('A102 spur faces removed',len(dl),'endz %.3f spz %s'%(endz,spz))
# terrain cap under road+curbs, and lift lawn directly behind curbs to curb top (only if lower)
vs=[];tris=[]
for o in (ob,cW,cE):
    b0=len(vs); vs+=[o.matrix_world@v.co for v in o.data.vertices]
    for p_ in o.data.polygons: tris.append([b0+i for i in p_.vertices])
bvh=BVHTree.FromPolygons(vs,tris)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.data; nt=len(tm.vertices)
c2=np.empty(nt*3); tm.vertices.foreach_get('co',c2); c2=c2.reshape(-1,3); MT=np.array(T.matrix_world); TW=c2@MT[:3,:3].T+MT[:3,3]
sel=np.where((TW[:,0]>-262)&(TW[:,0]<-205)&(TW[:,1]>-250)&(TW[:,1]<-155))[0]; cap=0; lift=0
for k in sel:
    h=bvh.ray_cast(Vector((TW[k,0],TW[k,1],TW[k,2]+6)),Vector((0,0,-1)),14)
    if h[0] is not None:
        if TW[k,2]>h[0].z-0.05: TW[k,2]=h[0].z-0.05; cap+=1
dlt=[]
for k in sel:
    h=bvh.ray_cast(Vector((TW[k,0],TW[k,1],TW[k,2]+6)),Vector((0,0,-1)),14)
    if h[0] is not None: dlt.append(h[0].z-TW[k,2])
if dlt: print('A102 road-terrain gap under road: n %d med %.2f p95 %.2f max %.2f'%(len(dlt),np.median(dlt),np.percentile(dlt,95),max(dlt)))

# raise-only: terrain in the 3 m bands outside each road edge up to 2023 LiDAR (walk/verge levels; LiDAR step 12-20 cm)
lg=np.load(B+'lidgrid102.npz'); LG=lg['G']; GX,GY,GR=float(lg['X0']),float(lg['Y0']),float(lg['R'])
def lidxy(x,y):
    i=int(round((x-GX)/GR)); j=int(round((y-GY)/GR))
    if 0<=j<LG.shape[0] and 0<=i<LG.shape[1]:
        v=LG[j-1:j+2,i-1:i+2]; v=v[np.isfinite(v)]; return float(np.median(v)) if len(v) else None
    return None
SSf=np.arange(-1,S1+1.01,0.5); FR=[frame(s) for s in SSf]; PP=np.array([f[0] for f in FR]); NN=np.array([f[1] for f in FR])
raised=0
for k in sel:
    q=TW[k,:2]; dd=np.hypot(*(PP-q).T); a=int(np.argmin(dd)); s=SSf[a]
    if s<1 or s>S1-1: continue
    o=(q-PP[a])@NN[a]; e=eE(s)
    if (e-3.0<o<e-0.15) or (EW+0.15<o<EW+3.0):
        t=lidxy(*q)
        if t is not None and TW[k,2]<t-0.03 and t-TW[k,2]<0.8: TW[k,2]=t-0.01; raised+=1
print('A102 terrain raised beside road',raised)
Mi=np.linalg.inv(MT); tm.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); tm.update()
print('A102 terrain capped',cap)
# report other meshes poking above the new road (excluding GN objects)
pk={}
for o in bpy.data.objects:
    if o.type!='MESH' or o in (ob,cW,cE,T,sp) or o.name.startswith('WS27'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<-262 or min(xs)>-205 or max(ys)<-250 or min(ys)>-155: continue
    n_=0
    for v in o.data.vertices[:20000]:
        w_=o.matrix_world@v.co; h=bvh.ray_cast(Vector((w_.x,w_.y,w_.z+6)),Vector((0,0,-1)),14)
        if h[0] is not None and w_.z>h[0].z+0.01 and w_.z<h[0].z+1.0: n_+=1
    if n_: pk[o.name]=n_
print('A102 pokes',pk)
json.dump(dict(endz=endz,spz=spz,spur_removed=len(dl),cap=cap,pokes=pk,verts=len(me.vertices)),open(B+'applied102.json','w'),indent=1)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A102 SAVED')

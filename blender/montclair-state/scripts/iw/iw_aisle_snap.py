# Session iw (2026-10-25 ~6:30 PM ET): tidy the aisle-junction creases on the Kasser amphitheater bowl.
# Session it snapped riser verts onto exact row contours but skipped any vertex touching an aisle face; iv's probe
# found ~450-535 seat/riser faces tilted 8-55 deg next to the aisles. Those faces hold row verts left at fractional
# (mid-riser) levels between the aisle's half-step verts. Here every non-aisle, non-outline vertex still at a fractional
# level within RING rings of an aisle vertex is moved along grad t onto its row contour (it's rule: upper half -> riser
# top at level ceil, lower half -> riser foot t=k+1-W at level floor) with a larger move cap; if the contour is too far it
# is just snapped vertically to the nearest level. Aisle verts (half-step profile) are not moved. Then remove_doubles,
# seat/riser material + brick-row UV v re-derived, smooth-by-angle 30 deg, it_rowpos recomputed.
# Order: ip -> iq -> ir -> is -> it -> iu -> iv -> iw. Env SAVE=1, DRY=1 (stats only), RING (default 2), MAXMV (x RES, default 0 = vertical-only; the contour targets sat ~0.54 m away so horizontal moves were rejected).
import bpy, bmesh, numpy as np, os, math
D='/workspace/nj-scenes/montclair-state/'
N_ROWS=19; Z_STAGE=132.45; Z_TOP=141.3; RISER=(Z_TOP-Z_STAGE)/N_ROWS; W=0.12; RES=0.08; SL=1
g=np.load(D+'north/data/day_heroes/cx/amphi/amphi_grid_0p5m_cx.npz'); G=g['ground'].astype(np.float64); x0=float(g['x0']); y0=float(g['y0']); R=float(g['res'])
s=1.2/R; r=int(3*s); k=np.exp(-0.5*(np.arange(-r,r+1)/s)**2); k/=k.sum()
Gp=np.pad(G,r,mode='edge'); Gs=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),1,Gp); Gs=np.apply_along_axis(lambda v:np.convolve(v,k,'valid'),0,Gs)
def samp(x,y):
    fx=(x-x0)/R-0.5; fy=(y-y0)/R-0.5; ix=np.clip(np.floor(fx).astype(int),0,G.shape[1]-2); iy=np.clip(np.floor(fy).astype(int),0,G.shape[0]-2)
    tx=np.clip(fx-ix,0,1); ty=np.clip(fy-iy,0,1)
    return (Gs[iy,ix]*(1-tx)*(1-ty)+Gs[iy,ix+1]*tx*(1-ty)+Gs[iy+1,ix]*(1-tx)*ty+Gs[iy+1,ix+1]*tx*ty)
def T(x,y): return (samp(x,y)-Z_STAGE-0.06)/RISER+1.0
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[m.name if m else None for m in me.materials]
SEATI=names.index('hn_amphi_seat_stone_blocks'); RIS=names.index('hn_amphi_riser_coursed_stone')
AIS=set(i for i,n in enumerate(names) if n and 'aisle' in n)
def crease_count():
    n=np.empty(len(me.polygons)*3); me.polygons.foreach_get('normal',n); n=n.reshape(-1,3)
    mi=np.empty(len(me.polygons),int); me.polygons.foreach_get('material_index',mi)
    av=set()
    for p in me.polygons:
        if p.material_index in AIS: av.update(p.vertices)
    tl=np.degrees(np.arccos(np.clip(n[:,2],-1,1))); c=[0,0]; a=[0.0,0.0]
    for p in me.polygons:
        if mi[p.index] in (SEATI,RIS) and 8<tl[p.index]<55:
            k=0 if any(v in av for v in p.vertices) else 1; c[k]+=1; a[k]+=p.area
    return c,[round(x,2) for x in a]
print('IW before crease faces [near_aisle, elsewhere]',*crease_count())
RING=int(os.environ.get('RING',2))
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
bnd=set(v.index for v in bm.verts if v.is_boundary)
aisle=set(v.index for v in bm.verts if any(f.material_index in AIS for f in v.link_faces))
near=set(aisle); front=set(aisle)
for _ in range(RING):
    nf=set()
    for i in front:
        for e in bm.verts[i].link_edges: nf.add(e.other_vert(bm.verts[i]).index)
    front=nf-near; near|=nf
cand=[]
for i in near:
    if i in aisle or i in bnd: continue
    v=bm.verts[i]; l=(v.co.z-Z_STAGE)/RISER; f=l-math.floor(l+1e-6)
    if 1e-3<f<0.999: cand.append(v)
print('IW cand (fractional row verts within',RING,'rings of aisle)',len(cand))
co=np.array([v.co[:] for v in cand]); x,y=co[:,0],co[:,1]
t=T(x,y); lev=(co[:,2]-Z_STAGE)/RISER
e=0.02; gx=(T(x+e,y)-T(x-e,y))/(2*e); gy=(T(x,y+e)-T(x,y-e))/(2*e); g2=gx*gx+gy*gy+1e-12
L0=np.floor(lev+1e-6); fr=lev-L0; up=fr>=0.5
Lf=np.where(up,L0+1,L0); tt=np.where(up,L0+1,L0+1-W)
dt=tt-t; dx=dt*gx/g2; dy=dt*gy/g2; mv=np.hypot(dx,dy)
MAXMV=float(os.environ.get('MAXMV',0))*RES; ok=mv<MAXMV
print('IW mv pct',[round(float(np.percentile(mv,q)),3) for q in (50,75,90,95,99)],'ok',int(ok.sum()),'vertical-only',int((~ok).sum()))
if os.environ.get('DRY')!='1':
    for i,v in enumerate(cand):
        if ok[i]: v.co.x=x[i]+dx[i]; v.co.y=y[i]+dy[i]
        v.co.z=Z_STAGE+Lf[i]*RISER
    nb=len(bm.verts); bmesh.ops.remove_doubles(bm,verts=cand,dist=0.012)
    bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=1e-4)
    print('IW merged',nb-len(bm.verts))
    uvl=bm.loops.layers.uv.active; nre=0
    for f in bm.faces:
        if f.material_index not in (SEATI,RIS): continue
        lv_=[(v.co.z-Z_STAGE)/RISER for v in f.verts]; mi=RIS if (max(lv_)-min(lv_))>0.06 else SEATI
        if mi!=f.material_index: f.material_index=mi; nre+=1
        for lp in f.loops: lp[uvl].uv.y=(lp.vert.co.z-Z_STAGE)/RISER+0.5
    print('IW faces re-assigned',nre)
    bm.to_mesh(me); bm.free(); me.update(); me.set_sharp_from_angle(angle=math.radians(30))
    n_=np.empty(len(me.polygons)*3); me.polygons.foreach_get('normal',n_); a_=np.empty(len(me.polygons)); me.polygons.foreach_get('area',a_)
    print('IW down-facing',int((n_.reshape(-1,3)[:,2]<0).sum()),'down&big',int(((n_.reshape(-1,3)[:,2]<0)&(a_>1e-4)).sum()))
    n=len(me.vertices); c=np.empty(n*3); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    tv=T(c[:,0],c[:,1]); lv=np.round((c[:,2]-Z_STAGE)/RISER,4); rp=np.clip(tv-np.floor(lv+1e-4),0,1)
    me.attributes['it_rowpos'].data.foreach_set('value',rp.astype(np.float32))
    print('IW after crease faces [near_aisle, elsewhere]',*crease_count())
    ob['iw_aisle_snap']='2026-10-25 session iw: aisle-adjacent row verts snapped to row contours'
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IW SAVED')

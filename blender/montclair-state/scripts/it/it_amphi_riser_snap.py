# Session it (2026-10-25 ~3:30 PM ET): straighten the ragged riser edges of the Kasser amphitheater bowl.
# The bowl is an 8 cm grid whose row levels are quantised from the smoothed LiDAR ground (ip build, prof()). The riser
# lines therefore step around the curve with the grid (the ragged near-row strip in the close-ups). Here every vertex on a
# riser face (not aisle, not outline) is moved along the gradient of the continuous row coordinate t onto the exact
# contour (bottom of riser t=k+1-W, top of riser t=k+1), z snapped to that level, so each riser edge is a smooth arc.
# Also writes a POINT float attribute 'it_rowpos' (t minus final level: 0 at a seat-front edge, ~0.88 at the riser foot)
# and adds a position-based front-edge wear band (shader nodes labelled it_*) on the seat/riser stone.
# Order: ip build -> iq -> ir -> is -> it. Env SAVE=1, DRY=1 (stats only).
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
M=np.array(ob.matrix_world); print('IT matrix identity?',np.allclose(M,np.eye(4)))
names=[m.name if m else None for m in me.materials]; print('IT mats',names)
RIS=names.index('hn_amphi_riser_coursed_stone') if 'hn_amphi_riser_coursed_stone' in names else 2
AIS=set(i for i,n in enumerate(names) if n and ('aisle' in n))|{4}
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
bnd=set(v.index for v in bm.verts if v.is_boundary)
cand=[]
for v in bm.verts:
    if v.index in bnd: continue
    fm=[f.material_index for f in v.link_faces]
    if any(m in AIS for m in fm): continue
    if RIS in fm: cand.append(v)
co=np.array([v.co[:] for v in cand]); x,y=co[:,0],co[:,1]
t=T(x,y); lev=np.round((co[:,2]-Z_STAGE)/RISER,3)  # current level (fractional on mid-riser verts)
e=0.02; gx=(T(x+e,y)-T(x-e,y))/(2*e); gy=(T(x,y+e)-T(x,y-e))/(2*e); g2=gx*gx+gy*gy+1e-12
L0=np.floor(lev+1e-6); fr=lev-L0
up=fr>=0.5; Lf=np.where(up,L0+1,L0)          # final level
# target t: top of riser (upper edge) = Lf ; bottom of riser (lower edge) = Lf+1-W
tt=np.where(up|(fr>0.5),Lf,Lf+1-W)
# decide lower vs upper for flat verts: a flat vert on a riser face is the upper edge if its t is near its level (just above integer), else lower
flat=fr<1e-3
dl=np.abs(t-(L0+1-W)); du=np.abs(t-L0)
tt=np.where(flat&(du<dl),L0,np.where(flat,L0+1-W,tt)); Lf=np.where(flat,L0,Lf)
dt=tt-t; dx=dt*gx/g2; dy=dt*gy/g2; mv=np.hypot(dx,dy)
MAXMV=float(os.environ.get('MAXMV',1.5))*RES; ok=mv<MAXMV
print('IT mv pct',[round(float(np.percentile(mv,q)),3) for q in (50,75,90,95,99)],'m/row med %.2f'%np.median(1/np.sqrt(g2)))
print('IT cand',len(cand),'move ok',int(ok.sum()),'too far',int((~ok).sum()),'move median %.3f p95 %.3f'%(np.median(mv[ok]),np.percentile(mv[ok],95)))
if os.environ.get('DRY')!='1':
    if os.environ.get('NOSNAP')=='1': bm.free()
    else:
        for i,v in enumerate(cand):
            if os.environ.get('NOSNAP')=='1': break
            if ok[i]: v.co.x=x[i]+dx[i]; v.co.y=y[i]+dy[i]; v.co.z=Z_STAGE+Lf[i]*RISER
        nb=len(bm.verts); bmesh.ops.remove_doubles(bm,verts=[v for i,v in enumerate(cand) if ok[i]],dist=0.012)
        bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=1e-4)
        sh=0
        for e in bm.edges:
            pass
        print('IT merged',nb-len(bm.verts),'sharp',sh)
        # re-derive seat/riser material and the brick-row UV v (= level + 0.5) from the snapped geometry
        uvl=bm.loops.layers.uv.active; SEATI=names.index('hn_amphi_seat_stone_blocks'); nre=0
        for f in bm.faces:
            if f.material_index not in (SEATI,RIS): continue
            lv_=[(v.co.z-Z_STAGE)/RISER for v in f.verts]; mi=RIS if (max(lv_)-min(lv_))>0.06 else SEATI
            if mi!=f.material_index: f.material_index=mi; nre+=1
            for lp in f.loops: lp[uvl].uv.y=(lp.vert.co.z-Z_STAGE)/RISER+0.5
        print('IT faces re-assigned',nre)
        bm.to_mesh(me); bm.free(); me.update(); me.set_sharp_from_angle(angle=math.radians(30))
        n_=np.empty(len(me.polygons)*3); me.polygons.foreach_get('normal',n_); a_=np.empty(len(me.polygons)); me.polygons.foreach_get('area',a_)
        print('IT down-facing',int((n_.reshape(-1,3)[:,2]<0).sum()),'down&big',int(((n_.reshape(-1,3)[:,2]<0)&(a_>1e-4)).sum()))
    # row-position attribute for every vertex
    n=len(me.vertices); c=np.empty(n*3); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    tv=T(c[:,0],c[:,1]); lv=np.round((c[:,2]-Z_STAGE)/RISER,4); rp=np.clip(tv-np.floor(lv+1e-4),0,1)
    if 'it_rowpos' in me.attributes: me.attributes.remove(me.attributes['it_rowpos'])
    a=me.attributes.new('it_rowpos','FLOAT','POINT'); a.data.foreach_set('value',rp.astype(np.float32))
    # shader: position band (front edge of each seat = rowpos ~0) on seat + riser stone
    for nm_,gain in [('hn_amphi_seat_stone_blocks',1.18),('hn_amphi_riser_coursed_stone',1.12)]:
        m=bpy.data.materials[nm_]; nt=m.node_tree
        b=[q for q in nt.nodes if q.bl_idname=='ShaderNodeBsdfPrincipled'][0]
        for q in [q for q in nt.nodes if q.label.startswith('it_')]:
            if q.label=='it_mix': nt.links.new(q.inputs[1].links[0].from_socket,b.inputs['Base Color'])
        for q in [q for q in nt.nodes if q.label.startswith('it_')]: nt.nodes.remove(q)
        src=b.inputs['Base Color'].links[0].from_socket
        def N(tp,lab): q=nt.nodes.new(tp); q.label=lab; return q
        at=N('ShaderNodeAttribute','it_attr'); at.attribute_name='it_rowpos'
        mr=N('ShaderNodeMapRange','it_band'); mr.inputs['From Min'].default_value=0.0; mr.inputs['From Max'].default_value=0.075
        mr.inputs['To Min'].default_value=1.0; mr.inputs['To Max'].default_value=0.0; mr.clamp=True; mr.interpolation_type='SMOOTHSTEP'
        nt.links.new(at.outputs['Fac'],mr.inputs['Value'])
        tc=N('ShaderNodeTexCoord','it_tc'); nz=N('ShaderNodeTexNoise','it_noise'); nz.inputs['Scale'].default_value=6.0; nz.inputs['Detail'].default_value=6
        nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
        nm=N('ShaderNodeMapRange','it_nmask'); nm.inputs['From Min'].default_value=0.3; nm.inputs['From Max'].default_value=0.62; nm.inputs['To Min'].default_value=0.45; nm.clamp=True
        nt.links.new(nz.outputs['Fac'],nm.inputs['Value'])
        mm=N('ShaderNodeMath','it_m'); mm.operation='MULTIPLY'; nt.links.new(mr.outputs[0],mm.inputs[0]); nt.links.new(nm.outputs[0],mm.inputs[1])
        mx=N('ShaderNodeMixRGB','it_mix'); mx.blend_type='MULTIPLY'; mx.inputs[2].default_value=(gain,gain*0.99,gain*0.975,1)
        nt.links.new(mm.outputs[0],mx.inputs[0]); nt.links.new(src,mx.inputs[1]); nt.links.new(mx.outputs[0],b.inputs['Base Color'])
        print('IT band',nm_)
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IT SAVED')

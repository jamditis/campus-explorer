# Session iz (2026-10-25 ~9:30 PM ET): per-block length jitter WITHIN each row (on top of iy's per-row length).
# Same as iy_block_len.py, but u is warped monotonically per row: u' = u + J*(0.10*sin(2pi*u/2.3+p1) + 0.07*sin(2pi*u/3.7+p2)),
# random phases per row (seed SEED+1000). Max du'/du deviation = J*0.39 (default J=1 -> block lengths vary about +-35% around
# the row's BL, never folding). Joints stay radial (u depends only on theta and the row). Env JIT (default 1.0; 0 = iy exactly).
# Order: ... -> iz_aisle_cheeks -> iy_wedge_normals -> iz_block_jitter (replaces iy_block_len). REVERT=1 restores ix UVs as before.
# Session iy (2026-10-25 ~8:30 PM ET): per-row block-length variation for the amphitheater seat/riser/aisle joints.
# Same as ix_radial_uv.py (U = theta * R_row / BL, V = level+0.5, joints radial and continuous along each row) but BL is
# now chosen per row level from a fixed seed in [BLMIN, BLMAX] (default 1.5-2.1 m), so the joint rhythm changes row to row
# instead of identical 1.8 m blocks everywhere. Rows keep the brick half-offset of the Brick Texture.
# Run after ... -> ix -> iy_wedge_normals -> iy_wedge_shade. Env SAVE=1, OUTB=copy, DRY=1 stats, SEED (default 25),
# BLMIN/BLMAX. REVERT=1 restores ix's UVs from UV layer 'UVMap_pre_iy' (pre-ix UVs stay in 'UVMap_pre_ix').
# Session ix (2026-10-25): fix the faint zig-zag dark marks inside the amphitheater seat stones.
# Cause: the brick-joint U coordinate came from ip's build (u = theta*r/BL at the ORIGINAL 8 cm grid positions).
#  (a) it/iw snapped ~37k verts but only re-derived V, so U kept pre-snap values -> the vertical mortar lines
#      (Brick Texture mortar + its bump + per-block white noise) kink at every moved vertex -> zig-zags;
#  (b) u = theta*r makes joints slant across the seat depth (not radial), so each joint line crosses many 8 cm
#      cells and every per-vertex error shows as a step.
# Fix: U re-derived from CURRENT vertex positions as theta * R_row / BL, with R_row a constant per row level
#  (median radius of that level's seat verts), so joints are true radial cuts, continuous across faces and
#  independent of the grid. V re-derived as before. Applies to seat, riser and aisle stone faces.
# Run after ip -> iq -> ir -> is -> it -> iu -> iv -> iw. SAVE=1 saves; OUTB=path saves a copy; DRY=1 stats only.
# Old UVs stored in UV layer 'UVMap_pre_iy' (REVERT=1 copies them back).
import bpy, bmesh, math, os, numpy as np
N_ROWS=19; Z_STAGE=132.45; Z_TOP=141.3; RISER=(Z_TOP-Z_STAGE)/N_ROWS
rng=np.random.default_rng(int(os.environ.get('SEED',25))); BLMIN=float(os.environ.get('BLMIN',1.5)); BLMAX=float(os.environ.get('BLMAX',2.1))
BLK={k:round(float(rng.uniform(BLMIN,BLMAX)),3) for k in range(-2,N_ROWS+3)}; print('IY BL per row',BLK)
JIT=float(os.environ.get('JIT',1.0)); _r2=np.random.default_rng(int(os.environ.get('SEED',25))+1000); PH={k:(float(_r2.uniform(0,6.2832)),float(_r2.uniform(0,6.2832))) for k in BLK}
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data; ob['iz_block_jitter']='2026-10-25 session iz: per-block length jitter within rows (UV warp)'
names=[s.material.name if s.material else '' for s in ob.material_slots]; print('IY slots',names)
SEAT=names.index('hn_amphi_seat_stone_blocks'); RIS=names.index('hn_amphi_riser_coursed_stone'); AIS=names.index('io_amphi_aisle_stone')
if 'UVMap_pre_iy' not in me.uv_layers:
    nl=me.uv_layers.new(name='UVMap_pre_iy'); src=me.uv_layers['UVMap']
    buf=np.empty(len(me.loops)*2); src.data.foreach_get('uv',buf); nl.data.foreach_set('uv',buf)
me.uv_layers.active=me.uv_layers['UVMap']
for l in me.uv_layers: l.active_render=(l.name=='UVMap')
if os.environ.get('REVERT'):
    buf=np.empty(len(me.loops)*2); me.uv_layers['UVMap_pre_iy'].data.foreach_get('uv',buf); me.uv_layers['UVMap'].data.foreach_set('uv',buf); print('IY REVERTED')
else:
    bm=bmesh.new(); bm.from_mesh(me); uvl=bm.loops.layers.uv['UVMap']
    # stage centre = mean of stage-level verts (z within 2 cm of the stage level)
    st=np.array(list({v.index:v.co[:2] for f in bm.faces if f.material_index==names.index('io_amphi_stage_concrete') for v in f.verts}.values()))
    CX,CY=st.mean(0); print('IY centre (stage-face verts)',round(CX,2),round(CY,2),len(st))
    sv=np.array([v.co[:2] for f in bm.faces if f.material_index==SEAT for v in f.verts])
    TH0=math.atan2((sv[:,1]-CY).mean(),(sv[:,0]-CX).mean()); print('IY bowl mean dir',round(TH0,3))
    rs={}
    for f in bm.faces:
        if f.material_index!=SEAT: continue
        for v in f.verts:
            k=int(round((v.co.z-Z_STAGE)/RISER)); rs.setdefault(k,[]).append(math.hypot(v.co.x-CX,v.co.y-CY))
    R={k:float(np.median(a)) for k,a in rs.items()}; print('IY R_row',{k:round(r,2) for k,r in sorted(R.items())})
    ks=sorted(R)
    def Rk(k):
        if k in R: return R[k]
        return R[min(ks,key=lambda q:abs(q-k))]
    th_all=[]; du=[]; n=0
    for f in bm.faces:
        if f.material_index not in (SEAT,RIS,AIS): continue
        lv=[(v.co.z-Z_STAGE)/RISER for v in f.verts]
        k=int(math.floor(min(lv)+0.25)) if f.material_index!=SEAT else int(round(sum(lv)/len(lv)))
        rr=Rk(k)
        # theta continuous across the face (no wrap inside a face)
        for lp in f.loops:
            v=lp.vert; th=(math.atan2(v.co.y-CY,v.co.x-CX)-TH0+math.pi)%(2*math.pi)-math.pi; th_all.append(th)
            u=th*rr/BLK.get(k,1.8); p1,p2=PH.get(k,(0.0,0.0)); u=u+JIT*(0.10*math.sin(2*math.pi*u/2.3+p1)+0.07*math.sin(2*math.pi*u/3.7+p2))
            du.append(abs(u-lp[uvl].uv.x))
            if os.environ.get('DRY')!='1': lp[uvl].uv=(u,(v.co.z-Z_STAGE)/RISER+0.5)
        n+=1
    th_all=np.array(th_all); du=np.array(du)
    print('IY faces',n,'theta range',round(float(th_all.min()),3),round(float(th_all.max()),3),'|du| pct50/90/99',[round(float(np.percentile(du,q)),3) for q in (50,90,99)])
    if os.environ.get('DRY')!='1': bm.to_mesh(me)
    bm.free(); me.update()
# per-block noise & brick both read 'UVMap' -> nothing else to change in the shaders
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('IY WROTE')
elif os.environ.get('SAVE'): bpy.ops.wm.save_mainfile(); print('IY SAVED')

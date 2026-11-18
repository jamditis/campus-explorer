# Session jc (2026-10-26 ~12:35 AM ET): fix the faint diagonal streaks on the amphitheater's lower aisle-step risers.
# Cause: iz_block_jitter picks the row level k (-> R_row, block length, jitter phase) PER FACE (riser: floor(min level+0.25)).
# Triangles of one riser plane around the aisle half-steps / chamfer corners can land on different k, so U jumps across
# their shared edge and the per-block tone + joints change inside one riser -> lighter/darker diagonal triangles.
# Fix: flood-fill connected near-vertical stone faces (|n.z|<0.5) across edges whose face normals agree (dot > 0.9, i.e.
# the same riser plane; cheeks are perpendicular so they stay separate), give each patch ONE k = floor(min level of patch
# + 0.25), and re-derive U exactly like iz (theta*R_k/BL_k + jitter); V unchanged (z-based). Run after iz_block_jitter.
# Env DRY=1 stats, SAVE=1, OUTB=copy. Revert: re-run iz_block_jitter.py.
import bpy, bmesh, math, os, numpy as np
N_ROWS=19; Z_STAGE=132.45; Z_TOP=141.3; RISER=(Z_TOP-Z_STAGE)/N_ROWS
rng=np.random.default_rng(int(os.environ.get('SEED',25))); BLMIN=float(os.environ.get('BLMIN',1.5)); BLMAX=float(os.environ.get('BLMAX',2.1))
BLK={k:round(float(rng.uniform(BLMIN,BLMAX)),3) for k in range(-2,N_ROWS+3)}
JIT=float(os.environ.get('JIT',1.0)); _r2=np.random.default_rng(int(os.environ.get('SEED',25))+1000); PH={k:(float(_r2.uniform(0,6.2832)),float(_r2.uniform(0,6.2832))) for k in BLK}
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SEAT=names.index('hn_amphi_seat_stone_blocks'); STAGE=names.index('io_amphi_stage_concrete')
STONE={i for i,n in enumerate(names) if n in ('hn_amphi_seat_stone_blocks','hn_amphi_riser_coursed_stone','io_amphi_aisle_stone','ip_amphi_aisle_nosing_worn')}
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); uvl=bm.loops.layers.uv['UVMap']; bm.faces.ensure_lookup_table()
st=np.array(list({v.index:v.co[:2] for f in bm.faces if f.material_index==STAGE for v in f.verts}.values())); CX,CY=st.mean(0)
sv=np.array([v.co[:2] for f in bm.faces if f.material_index==SEAT for v in f.verts]); TH0=math.atan2((sv[:,1]-CY).mean(),(sv[:,0]-CX).mean())
rs={}
for f in bm.faces:
    if f.material_index!=SEAT: continue
    for v in f.verts: rs.setdefault(int(round((v.co.z-Z_STAGE)/RISER)),[]).append(math.hypot(v.co.x-CX,v.co.y-CY))
R={k:float(np.median(a)) for k,a in rs.items()}; ks=sorted(R)
Rk=lambda k: R[k] if k in R else R[min(ks,key=lambda q:abs(q-k))]
isv=lambda f: f.material_index in STONE and abs(f.normal.z)<0.5
seen=set(); patches=[]
for f in bm.faces:
    if f.index in seen or not isv(f): continue
    stack=[f]; seen.add(f.index); P=[]
    while stack:
        g=stack.pop(); P.append(g)
        for e in g.edges:
            for h in e.link_faces:
                if h.index in seen or not isv(h): continue
                if g.normal.dot(h.normal)<0.9: continue
                seen.add(h.index); stack.append(h)
    patches.append(P)
chg=0; nf=0; mx=0.0
for P in patches:
    k_old={int(math.floor(min((v.co.z-Z_STAGE)/RISER for v in g.verts)+0.25)) for g in P}
    if len(k_old)<=1: continue
    k=int(math.floor(min((v.co.z-Z_STAGE)/RISER for g in P for v in g.verts)+0.25)); rr=Rk(k); chg+=1
    for g in P:
        nf+=1
        for lp in g.loops:
            v=lp.vert; th=(math.atan2(v.co.y-CY,v.co.x-CX)-TH0+math.pi)%(2*math.pi)-math.pi
            u=th*rr/BLK.get(k,1.8); p1,p2=PH.get(k,(0.0,0.0)); u=u+JIT*(0.10*math.sin(2*math.pi*u/2.3+p1)+0.07*math.sin(2*math.pi*u/3.7+p2))
            mx=max(mx,abs(u-lp[uvl].uv.x))
            if os.environ.get('DRY')!='1': lp[uvl].uv=(u,lp[uvl].uv.y)
print('JCU vertical patches',len(patches),'mixed-k patches unified',chg,'faces re-UVed',nf,'max |du|',round(mx,3))
if os.environ.get('DRY')!='1': bm.to_mesh(me); ob['jc_riser_uv']=f'2026-10-26 session jc: {chg} riser patches unified to one row k ({nf} faces)'
bm.free(); me.update()
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JCU WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JCU SAVED')

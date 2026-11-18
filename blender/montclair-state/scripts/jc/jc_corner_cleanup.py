# Session jc (2026-10-26 ~12:35 AM ET): clean jb's unclamped-bevel overlaps at the amphitheater aisle-cheek corners
# and the faint streaks on the lower aisle-step risers (Kasser_amphitheater_bowl_hl, MAIN).
# (1) Down-facing faces (n.z < -0.05; 188 after jb, median 1.8 cm2, total 0.097 m2) are fold-overs where the 1.8 cm
#     chamfer offset crossed a tiny neighbouring grid edge. Each small one (< MAXA cm2, not base fieldstone) is collapsed to
#     its centroid (bmesh pointmerge), iterated, then dissolve_degenerate. Horizontal folds keep their z, so seats don't move.
# (2) Streaks = non-planar riser/cheek n-gons (up to ~11 cm out of plane at cheek corners; ~1.5k riser faces > 4 mm),
#     which render as differently-lit triangles. Shading fix: after iy_wedge_normals + iz_block_jitter re-run, every
#     non-planar (> NPMM mm) near-vertical stone face gets custom split normals = its best-fit (Newell) face normal, so it
#     shades as one flat stone face. Faces tagged int face attr jc_flatn=1.
# (3) FLATALL=1 (default): every non-up (n.z<=0.9) stone face except iy wedges gets flat custom normals (its own face normal),
#     because the streaks turned out to be smooth-shading fans from tilted chamfer/corner faces bleeding into the risers.
#     jc_riser_uv.py also runs after iz (one row k per riser plane, removes U jumps inside a riser).
# Order: ... -> jb_nosing_chamfer (-> iy -> iz -> jb_chamfer_shade) -> jc_corner_cleanup (-> iy -> iz -> jc normals).
# Remaining slightly overhanging near-vertical cheek faces (n.z<-0.02, |n.z|<0.65) get horizontal custom normals.
# Env: MAXA (default 40 cm2), MAXH (horizontal folds, default 80 cm2), NPMM (default 3), DRY=1, OUTB=copy path, SAVE=1. Revert = backup montclair_state_pre_20261026jc.blend.
import bpy, bmesh, numpy as np, os, math, runpy
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
BASE=names.index('hn_amphi_base_fieldstone')
MAXA=float(os.environ.get('MAXA',40))*1e-4; NPMM=float(os.environ.get('NPMM',3))/1000; MAXH=float(os.environ.get('MAXH',80))*1e-4  # flat (horizontal) folds up to 80 cm2
if me.has_custom_normals:
    try: me.free_normals_split()
    except Exception: pass
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
d0=sum(1 for f in bm.faces if f.normal.z<-0.05); f0=len(bm.faces); merged=0
for it in range(4):
    bm.faces.ensure_lookup_table()
    down=[f for f in bm.faces if f.is_valid and f.normal.z<-0.05 and f.material_index!=BASE and (f.calc_area()<MAXA or (f.normal.z<-0.9 and f.calc_area()<MAXH))]
    if not down: break
    used=set()
    for f in down:
        if not f.is_valid: continue
        vs=[v for v in f.verts]
        if any(v in used for v in vs): continue
        c=sum((v.co for v in vs),vs[0].co*0)/len(vs)
        used.update(vs)
        bmesh.ops.pointmerge(bm,verts=vs,merge_co=c); merged+=1
    bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=5e-4); bm.normal_update()
    print('JC iter',it,'collapsed so far',merged,'down now',sum(1 for f in bm.faces if f.normal.z<-0.05))
d1=sum(1 for f in bm.faces if f.normal.z<-0.05); dA=sum(f.calc_area() for f in bm.faces if f.normal.z<-0.05)
nm=sum(1 for e in bm.edges if len(e.link_faces)>2)
print('JC down-facing',d0,'->',d1,'remaining area m2',round(dA,4),'faces',f0,'->',len(bm.faces),'nonmanifold edges',nm)
if os.environ.get('DRY')=='1':
    bm.free()
else:
    bm.to_mesh(me); bm.free(); me.update(); me.set_sharp_from_angle(angle=math.radians(30))
    sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
    S='/workspace/nj-scenes/montclair-state/scripts/'
    runpy.run_path(S+'iy/iy_wedge_normals.py',run_name='__main__')
    runpy.run_path(S+'iz/iz_block_jitter.py',run_name='__main__')
    runpy.run_path(S+'jc/jc_riser_uv.py',run_name='__main__')   # one row k per riser plane (UV streak fix)
    for k,v in sv.items():
        if v is not None: os.environ[k]=v
    # (2) flat custom normals on non-planar near-vertical stone faces
    P=len(me.polygons); L=len(me.loops)
    cn=np.empty(L*3); me.corner_normals.foreach_get('vector',cn); cn=cn.reshape(-1,3)
    co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    wed=np.zeros(P,np.int32)
    if me.attributes.get('iy_wedge'): me.attributes['iy_wedge'].data.foreach_get('value',wed)
    FLATALL=os.environ.get('FLATALL','1')=='1'
    STONE={i for i,nm in enumerate(names) if nm in ('hn_amphi_seat_stone_blocks','hn_amphi_riser_coursed_stone','io_amphi_aisle_stone','ip_amphi_aisle_nosing_worn','io_amphi_stage_concrete')}
    flag=np.zeros(P,np.int32); nfl=0
    for p in me.polygons:
        if p.material_index==BASE or wed[p.index]: continue
        n=np.array(p.normal)
        if FLATALL:
            if n[2]>0.9 or p.material_index not in STONE: continue
        elif abs(n[2])>0.65: continue
        pts=co[list(p.vertices)]; c=pts.mean(0)
        over=n[2]<-0.02 and abs(n[2])<0.65   # slightly overhanging cheek faces left by the merge -> shade as vertical
        if not FLATALL and not over and (p.loop_total<4 or np.abs((pts-c)@n).max()<=NPMM): continue
        if over: n=np.array([n[0],n[1],0.0]); n=n/max(np.linalg.norm(n),1e-9)
        for li in p.loop_indices: cn[li]=n
        flag[p.index]=1; nfl+=1
    me.normals_split_custom_set(cn.tolist())
    a=me.attributes.get('jc_flatn') or me.attributes.new('jc_flatn','INT','FACE'); a.data.foreach_set('value',flag); me.update()
    print('JC flat-normal faces',nfl)
    ob['jc_corner_cleanup']=f'2026-10-26 session jc: {merged} fold-over faces collapsed (down-facing {d0}->{d1}); {nfl} non-planar riser faces flat custom normals'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JC WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JC SAVED')

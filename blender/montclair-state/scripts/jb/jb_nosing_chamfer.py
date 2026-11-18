# Session jb (2026-10-25 ~11:30 PM ET): small real chamfer on the bench (seat) front nosings and the aisle step nosings
# of the Kasser amphitheater bowl (Kasser_amphitheater_bowl_hl).
# Edge selection: manifold edges between an UP face (n.z > 0.9; seat or aisle tread) and a near-vertical face (|n.z| < 0.35;
# riser / cheek) where the vertical face hangs BELOW the edge (convex nosing). Concave seat-back junctions are skipped.
# Outline / stage / base-fieldstone edges are skipped. bmesh bevel, offset OFF (default 0.018 m), 1 segment, NO clamp_overlap
# (clamp collapsed every chamfer to 0 width because of tiny neighbouring grid edges; CLAMP=1 to re-enable).
# New chamfer faces get the material of the adjacent up face and int face attribute jb_chamfer=1 (shader: slight lighter/worn tone
# via jb_chamfer_shade nodes, see below). Custom normals are freed first; afterwards iy_wedge_normals.py and iz_block_jitter.py
# are re-run (same as ja) so wedge normals and UVs follow the new topology.
# Order: ... -> ja_aisle_treads -> iy_wedge_normals -> iz_block_jitter -> jb_nosing_chamfer (re-runs iy_wedge_normals + iz_block_jitter).
# Env: DRY=1 stats only; OFF=metres; OUTB=copy path; SAVE=1. Revert = backup montclair_state_pre_20261025jb.blend (topology change).
import bpy, bmesh, numpy as np, os, math, runpy
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
print('JB mats',names)
BASE=names.index('hn_amphi_base_fieldstone'); STAGE=names.index('io_amphi_stage_concrete')
OFF=float(os.environ.get('OFF',0.018))
if me.has_custom_normals:
    try: me.free_normals_split()
    except Exception: pass
bm=bmesh.new(); bm.from_mesh(me)
lay=bm.faces.layers.int.get('jb_chamfer') or bm.faces.layers.int.new('jb_chamfer')
bm.normal_update(); bm.edges.ensure_lookup_table()
sel=[]; cnt={}
for e in bm.edges:
    if len(e.link_faces)!=2 or e.is_boundary: continue
    f1,f2=e.link_faces
    if any(f.material_index in (BASE,STAGE) for f in (f1,f2)): continue
    up=[f for f in (f1,f2) if f.normal.z>0.9]; vt=[f for f in (f1,f2) if abs(f.normal.z)<0.35]
    if len(up)!=1 or len(vt)!=1: continue
    if e.calc_length()<0.02: continue
    zf=max(v.co.z for v in e.verts)
    other=[v.co.z for v in vt[0].verts if v not in e.verts]
    if not other or min(other)>zf-0.05: continue   # vertical face must hang below = convex nosing
    if max(other)>zf+0.01: continue
    sel.append(e); k=names[up[0].material_index]; cnt[k]=cnt.get(k,0)+1
L=sum(e.calc_length() for e in sel)
print('JB nosing edges',len(sel),'total length m',round(L,1),cnt)
if os.environ.get('DRY')=='1':
    bm.free()
else:
    upmat={}
    for e in sel:
        for f in e.link_faces:
            if f.normal.z>0.9: upmat[e.index]=f.material_index
    nf0=len(bm.faces)
    res=bmesh.ops.bevel(bm,geom=list(sel)+list({v for e in sel for v in e.verts}),offset=OFF,offset_type='OFFSET',segments=1,profile=0.5,
                        affect='EDGES',clamp_overlap=os.environ.get('CLAMP')=='1',loop_slide=True,harden_normals=False,mark_sharp=False)
    bm.faces.ensure_lookup_table(); newf=[f for f in res['faces'] if f.is_valid]; bm.normal_update()
    for f in bm.faces: f[lay]=0
    for f in newf: f[lay]=1
    # chamfer faces: give them the material of the neighbouring up face (seat / aisle tread)
    nch=0
    for f in newf:
        f[lay]=1; nch+=1
        best=None
        for e in f.edges:
            for g in e.link_faces:
                if g.is_valid and g is not f and g.normal.z>0.9: best=g.material_index
        if best is not None: f.material_index=best
    nd=len(bm.faces); bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=5e-4); bm.normal_update()
    down=sum(1 for f in bm.faces if f.normal.z<-0.05)
    print('JB chamfer faces',nch,'faces',nf0,'->',len(bm.faces),'dissolved',nd-len(bm.faces),'down-facing',down)
    bm.to_mesh(me); bm.free(); me.update(); me.set_sharp_from_angle(angle=math.radians(30))
    a=me.attributes.get('iy_wedge')
    if a: a.data.foreach_set('value',np.zeros(len(me.polygons),np.int32))
    ob['jb_nosing_chamfer']=f'2026-10-25 session jb: {OFF*100:.1f} cm chamfer on {len(sel)} seat/aisle nosing edges'
    sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
    S='/workspace/nj-scenes/montclair-state/scripts/'
    runpy.run_path(S+'iy/iy_wedge_normals.py',run_name='__main__')
    runpy.run_path(S+'iz/iz_block_jitter.py',run_name='__main__')
    if os.environ.get('JB_SHADE','1')=='1':
        runpy.run_path(S+'jb/jb_chamfer_shade.py',run_name='__main__')
    for k,v in sv.items():
        if v is not None: os.environ[k]=v
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JB WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JB SAVED')

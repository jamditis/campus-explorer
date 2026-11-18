# Session jg = jf_riser_plumb.py extended to the row-0 stage-front riser and aisle-cheek feet (backup montclair_state_pre_20261026jg.blend).
# (orig) Session jf EXPERIMENT (COPY ONLY unless clearly better): make the battered (~17-20 deg) bench risers plumb.
# Cause: it_amphi_riser_snap put each riser foot at t = k+1-W (W 0.12 rows ~ 15 cm toward the stage) under a riser top at t = k+1.
# Here: every riser-foot vertex (lower verts of non-chamfer riser faces with 0.12 < n.z < 0.6; not boundary, not touching
# aisle/base/stage faces) is moved horizontally back under the top edge by h*n.z/|n_h| along -n_h (averaged over its riser faces);
# verts on an aisle cheek line move only along the aisle axis s so the cheeks stay planar. Lower treads get ~15 cm deeper.
# Then jc_corner_cleanup MAXA=MAXH=0 (iy -> iz -> jc_riser_uv -> flat normals). Env DRY=1, OUTB=copy path, SAVE=1 (main; applied in jf after copy tests v1-v3).
import bpy, bmesh, math, os, runpy
from mathutils import Vector as V
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SKIP={names.index(n) for n in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete')}
AIS={i for i,n in enumerate(names) if 'aisle' in n}
RIS=names.index('hn_amphi_riser_coursed_stone')
if me.has_custom_normals:
    try: me.free_normals_split()
    except Exception: pass
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
def batt(f): return f.material_index==RIS and not f[CH] and 0.12<f.normal.z<0.6
nb0=sum(1 for f in bm.faces if batt(f)); A0=sum(f.calc_area() for f in bm.faces if batt(f))
mv={}
for f in bm.faces:
    if not batt(f): continue
    zs=[v.co.z for v in f.verts]; zt,zb=max(zs),min(zs); h=zt-zb
    if h<0.1: continue   # jg: the stage-front riser (row 0) is included now
    n=f.normal; nh=V((n.x,n.y,0)); L=nh.length
    if L<1e-3: continue
    d=-(nh/L)*(h*n.z/L)
    for v in f.verts:
        if v.co.z<zb+0.03: mv.setdefault(v,[]).append(d)
moved=0; skipped=0; cheek=0; orig={}
BASE=names.index('hn_amphi_base_fieldstone')
def oncheek(v):
    for ai in (0,1):
        s,dd=fr(v.co,ai)
        if s>0 and abs(abs(dd)-H)<0.006: return ai
    return None
# jg: stage-touching foot verts may move (stage is flat at the foot, horizontal move keeps it flat); aisle-touching foot verts
# may move only if they sit on an aisle cheek line (then along the aisle axis, so the aisle tread/cheek planes stay planar)
bad=set(v for v in mv if v.is_boundary or any(g.material_index==BASE for g in v.link_faces) or (any(g.material_index in AIS for g in v.link_faces) and oncheek(v) is None))
if os.environ.get('PROP','1')=='1':   # v2: a riser face with any skipped foot vert keeps all its foot verts (no half-moved warped faces)
    for f in bm.faces:
        if batt(f) and any(v in bad for v in f.verts): bad.update(v for v in f.verts if v in mv)
for v,ds in mv.items():
    if v in bad: skipped+=1; continue
    d=sum(ds,V((0,0,0)))/len(ds)
    if d.length>0.3: skipped+=1; continue
    ai=oncheek(v)
    if ai is not None:
        a=ATH[ai]; ax=V((math.cos(a),math.sin(a),0)); d=ax*(d.dot(ax)); cheek+=1
    orig[v]=(v.co.copy(),d.copy()); v.co+=d; moved+=1
bm.normal_update()
# v3: back off any moved foot vert whose linked faces now overhang/fold (n.z < -0.02): retry 75/50/25/0 % of its move
backed=0
for it in range(2):
    for v,(o,d) in orig.items():
        def badl(): 
            for g in v.link_faces: g.normal_update()
            return any(g.normal.z<-0.02 and g.material_index not in SKIP and g.calc_area()>1e-4 for g in v.link_faces)
        if not badl(): continue
        for fac in (0.75,0.5,0.25,0.0):
            v.co=o+d*fac
            if not badl(): break
        backed+=1
print('JFP backed off',backed)
bm.normal_update()
nb1=sum(1 for f in bm.faces if batt(f)); A1=sum(f.calc_area() for f in bm.faces if batt(f))
down=sum(1 for f in bm.faces if f.normal.z<-0.05 and f.material_index not in SKIP and f.calc_area()>2e-4)
WL=bm.faces.layers.int.get('iy_wedge')
def nbad():
    c=0
    for f in bm.faces:
        if f.material_index in SKIP or f[CH]: continue
        cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(cc,k)[1])-H))
        if fr(cc,ai)[0]<=0: continue
        ds=[fr(v.co,ai)[1] for v in f.verts]
        if any(abs(abs(d)-H)<0.01 for d in ds) and any(abs(d)<H-0.01 for d in ds) and all(abs(d)<=H+0.015 for d in ds):
            a=ATH[ai]; n=f.normal; nd=-n.x*math.sin(a)+n.y*math.cos(a)
            if (WL and f[WL]) or (abs(nd)>0.3 and (n.z>0.15 or n.z<-0.05)): c+=1
    return c
STG=names.index('io_amphi_stage_concrete')
print('JGP badcorner',nbad(),'stage faces tilted>0.02',sum(1 for f in bm.faces if f.material_index==STG and f.normal.z<0.98 and f.normal.z>0.3),'stage down',sum(1 for f in bm.faces if f.material_index==STG and f.normal.z<-0.05))
print('JFP moved',moved,'(cheek-constrained',cheek,') skipped',skipped,'battered riser faces',nb0,'->',nb1,'area m2 %.1f -> %.1f'%(A0,A1),'down>2cm2',down,'edges>2',sum(1 for e in bm.edges if len(e.link_faces)>2))
if os.environ.get('DRY')=='1': bm.free(); raise SystemExit
bm.to_mesh(me); bm.free(); me.update()
sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
os.environ['MAXA']='0'; os.environ['MAXH']='0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/jc/jc_corner_cleanup.py',run_name='__main__')
for k,v in sv.items():
    if v is not None: os.environ[k]=v
ob['jg_riser_plumb']=f'2026-10-26 session jg (stage-front riser + aisle-cheek feet): {moved} riser-foot verts moved back under the riser top (bench fronts plumb; was ~17-20 deg batter), {backed} backed off; battered riser faces {nb0}->{nb1}'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JFP WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JFP SAVED')

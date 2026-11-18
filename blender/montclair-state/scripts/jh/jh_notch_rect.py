# Session jh (2026-10-26 ~5:25 AM ET): aisle-foot notch in the plumb stage-front wall rebuilt as clean vertical rectangles.
# Problem (jg close-up CAM_closeup_amphitheater_stage_front_riser): where each aisle's bottom step cuts into the stage-front
# wall, the wall foot line was jagged (foot verts at the stage, z 132.916, up to ~22 cm toward the stage from the wall top)
# and the notch side faces were slanted fans, so they rendered as narrow dark triangles.
# Fix, per aisle (frame s along the aisle axis from (CX,CY), d across; cheek lines d=+-H):
#  (1) s_in = median s of the wall-top verts (z 133.355-133.37) inside the aisle; s_out(d) = interp. of the wall-top verts outside.
#  (2) every wall vert below the top (z < 133.355; foot + mid-height) inside the aisle -> s = s_in (plumb under the top);
#      outside within OUTW of the cheek -> s = s_out(d); on the cheek -> s clamped into [s_in, s_out].
#  (3) verts within CHW of a cheek line: foot/top verts -> d = +-H (rectangle corners); other wall verts whose s lies strictly
#      inside the notch span (between s_in and s_out) -> d = +-H (side face plane).
#  (4) per-vert revert if a linked stage/wall face flips or folds (n.z < -0.05, or stage n.z < 0.9); remove_doubles 4 mm on moved verts.
#  v2 (5:30 AM): seat-material floor faces at stage level (z 132.916) recoloured to stage concrete; floor-only verts behind the new foot line squashed onto it first (else the foot moves folded the stage and were reverted).
#  v3 (5:35 AM): floor faces attached to moved foot verts deleted, hole re-filled flat (holes_fill + beauty triangulate, stage concrete).
#  v5: both notch foot corners (s_in,+-H) and (s_out,+-H) guaranteed (nearest foot vert snapped) so each side face is a rectangle.
# Then jc_corner_cleanup MAXA=MAXH=0 (iy -> iz -> jc_riser_uv -> flat normals). Env DRY=1, OUTB=copy, SAVE=1.
import bpy, bmesh, math, os, runpy, statistics
from mathutils import Vector as V
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
OUTW=float(os.environ.get('OUTW',0.15)); CHW=float(os.environ.get('CHW',0.06)); CHWT=float(os.environ.get('CHWT',0.09))  # v4: wall-top notch corner verts up to 8 cm off the cheek
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
RIS=names.index('hn_amphi_riser_coursed_stone'); STG=names.index('io_amphi_stage_concrete'); BASE=names.index('hn_amphi_base_fieldstone')
SKIP={BASE,STG}; AIS={i for i,n in enumerate(names) if 'aisle' in n}
if me.has_custom_normals:
    try: me.free_normals_split()
    except Exception: pass
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); WL=bm.faces.layers.int.get('iy_wedge')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
def to(s,d,z,ai):
    a=ATH[ai]; return V((CX+s*math.cos(a)-d*math.sin(a), CY+s*math.sin(a)+d*math.cos(a), z))
def counts():
    def nbad():
        c=0
        for f in bm.faces:
            if f.material_index in SKIP or f[CH]: continue
            cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(cc,k)[1])-H))
            if fr(cc,ai)[0]<=0: continue
            ds=[fr(v.co,ai)[1] for v in f.verts]
            if any(abs(abs(d)-H)<0.01 for d in ds) and any(abs(d)<H-0.01 for d in ds) and all(abs(d)<=H+0.015 for d in ds):
                a=ATH[ai]; n=f.normal; nd=-n.x*math.sin(a)+n.y*math.cos(a)
                if (WL and f[WL]) or (abs(nd)>0.3 and (n.z>0.15 or n.z<-0.05)):
                    c+=1
                    if os.environ.get('DBG'): print('JHN badcorner',f.index,names[f.material_index][:12],tuple(round(x,2) for x in n),round(f.calc_area()*1e4,1),[(round(fr(w.co,ai)[0],3),round(fr(w.co,ai)[1],3),round(w.co.z,3)) for w in f.verts])
        return c
    bt=sum(1 for f in bm.faces if f.material_index==RIS and not f[CH] and 0.12<f.normal.z<0.6)
    return dict(bad=nbad(),batt=bt,down=sum(1 for f in bm.faces if f.normal.z<-0.05 and f.material_index not in SKIP and f.calc_area()>2e-4),
        stg_tilt=sum(1 for f in bm.faces if f.material_index==STG and 0.3<f.normal.z<0.98),stg_down=sum(1 for f in bm.faces if f.material_index==STG and f.normal.z<-0.05),
        nm=sum(1 for e in bm.edges if len(e.link_faces)>2),bnd=sum(1 for e in bm.edges if e.is_boundary),faces=len(bm.faces))
c0=counts(); print('JHN before',c0)
moved={}; nstg=[0]; ncorner=[0]
for ai in (0,1):
    a=ATH[ai]
    def nd_of(f): n=f.normal; return -n.x*math.sin(a)+n.y*math.cos(a)
    # aisle bottom-step riser s (aisle-adjacent riser faces at stage-touching region) -> wall region just in front of it
    wall=[]
    for f in bm.faces:
        if f.material_index!=RIS or f[CH]: continue
        zs=[v.co.z for v in f.verts]
        if min(zs)>132.93 or max(zs)>133.40 or abs(f.normal.z)>0.5: continue
        s,d=fr(f.calc_center_median(),ai)
        if abs(d)<H+0.35 and 8.0<s<9.5: wall.append(f)
    wv={v for f in wall for v in f.verts}
    tops=[(fr(v.co,ai),v) for v in wv if 133.355<=v.co.z<=133.37]
    tin=[sd[0] for sd,v in tops if abs(sd[1])<H-0.05]
    if not tin: print('JHN ai',ai,'no tops'); continue
    s_in=statistics.median(tin)
    print('JHN ai',ai,'wall faces',len(wall),'verts',len(wv),'s_in %.3f (n %d, range %.3f-%.3f)'%(s_in,len(tin),min(tin),max(tin)))
    for sg in (1,-1):
        to_=sorted((sd[1]*sg,sd[0]) for sd,v in tops if sd[1]*sg>H+0.004)
        if not to_: print('JHN ai',ai,'sg',sg,'no outside tops'); continue
        def s_out(u):
            # u = sg*d >= H; linear interp over outside tops sorted by u
            if u<=to_[0][0]: return to_[0][1]
            for (u0,s0),(u1,s1) in zip(to_,to_[1:]):
                if u0<=u<=u1: return s0+(s1-s0)*(u-u0)/max(u1-u0,1e-6)
            return to_[-1][1]
        so_H=s_out(H); lo,hi=min(s_in,so_H),max(s_in,so_H)
        print('JHN ai',ai,'sg',sg,'s_out(H) %.3f notch depth %.3f'%(so_H,so_H-s_in))
        # v2: stage-only verts (z 132.916) lying behind the planned wall foot line are squashed onto it first, so the
        # foot verts can move back without folding the stage faces that filled the old jagged foot wedges.
        for v in bm.verts:
            if v.co.z>132.93 or v.is_boundary or v in wv or not v.link_faces or any(g.normal.z<0.99 for g in v.link_faces): continue   # floor-only verts (stage or seat-material floor tris)
            s,d=fr(v.co,ai); u=d*sg
            if u<0 or abs(s-s_in)>0.35: continue
            if u<H-0.004: tgt=s_in
            elif u<=H+OUTW: tgt=s_out(u) if u>H+0.004 else max(s_in,so_H)
            else: continue
            if s>tgt-0.002 and s-tgt<0.3: moved[v]=(v.co.copy(),to(tgt,d,v.co.z,ai)); nstg[0]+=1
        for v in wv:
            if v.is_boundary or any(g.material_index==BASE for g in v.link_faces): continue
            s,d=fr(v.co,ai); u=d*sg
            if u<0: continue   # other side handled in its own pass (centre verts: u<0 for one sign) -- inside verts with |d| small handled by both? guard below
            z=v.co.z; ns,nd2=s,d
            foot=z<132.93; top=133.355<=z<=133.40
            if top and z>133.37 and u<H-0.004 and 0.005<abs(s-s_in)<0.04 and not any(g.material_index in AIS and g.normal.z<0.98 for g in v.link_faces):
                ns=s_in   # v2: stray chamfer-edge verts at the wall top (e.g. 8.903 vs 8.933) pulled onto the wall plane (else the plumbed foot overhangs)
            if not top:
                if u<H-0.004: ns=s_in
                elif u>H+0.004:
                    if u>H+OUTW: continue
                    ns=s_out(u)
                else: ns=min(max(s,lo),hi)
            if (abs(u-H)<CHW and foot) or (top and z<=133.385 and abs(u-H)<CHWT and not any(g.material_index in AIS and g.normal.z<0.98 for g in v.link_faces)):
                nd2=sg*H
            elif abs(u-H)<CHW and lo+0.008<ns<hi-0.008:
                nd2=sg*H
            if abs(ns-s)<5e-4 and abs(nd2-d)<5e-4: continue
            if abs(ns-s)>0.3: continue
            moved[v]=(v.co.copy(),to(ns,nd2,z,ai))
        # v5: make sure both rectangle foot corners exist on this cheek: cheek foot verts take the nearer of s_in / s_out(H);
        # if no foot vert sits at a corner, the nearest foot vert on that side (within 0.2 m) is snapped onto it.
        def tgt(v): return moved[v][1] if v in moved else v.co
        fe=[v for v in wv if v.co.z<132.93 and not v.is_boundary and not any(g.material_index==BASE for g in v.link_faces)]
        for v in fe:
            s,d=fr(tgt(v),ai)
            if abs(d*sg-H)<0.004:
                ns=s_in if abs(s-s_in)<=abs(s-so_H) else so_H
                moved[v]=(moved[v][0] if v in moved else v.co.copy(), to(ns,sg*H,v.co.z,ai))
        for side,sc in (('in',s_in),('out',so_H)):
            if any(abs(fr(tgt(v),ai)[1]*sg-H)<0.004 and abs(fr(tgt(v),ai)[0]-sc)<0.005 for v in fe): continue
            if side=='in': cand=[v for v in fe if H-0.2<fr(tgt(v),ai)[1]*sg<H-0.004]
            else: cand=[v for v in fe if H+0.004<fr(tgt(v),ai)[1]*sg<H+0.2]
            if not cand: print('JHN ai',ai,'sg',sg,'no',side,'corner candidate'); continue
            v=min(cand,key=lambda w:abs(fr(tgt(w),ai)[1]*sg-H))
            moved[v]=(moved[v][0] if v in moved else v.co.copy(), to(sc,sg*H,v.co.z,ai)); ncorner[0]+=1
    # centre verts with d==0 exactly would be handled by sg=1 (u>=0) only; fine.
for v,(o,n) in moved.items(): v.co=n
bm.normal_update()
def badv(v):
    for g in v.link_faces:
        g.normal_update()
        if g.calc_area()<1e-5: continue
        if all(abs(w.co.z-132.916)<0.003 for w in g.verts): continue   # v3: floor faces are re-filled below
        if g.normal.z<-0.05 and g.material_index not in SKIP and g.calc_area()>2e-4:
            if os.environ.get('DBG'): print('JHN badface',g.index,names[g.material_index][:12],round(g.normal.z,2),round(g.calc_area()*1e4,1),[tuple(round(c,3) for c in w.co) for w in g.verts])
            return True
    return False
rev=0
for it in range(2):
    for v,(o,n) in moved.items():
        if not badv(v): continue
        for fac in (0.5,0.0):
            v.co=o+(n-o)*fac
            if not badv(v): break
        rev+=1; print('JHN revert v%d'%v.index, tuple(round(c,3) for c in o), '->', tuple(round(c,3) for c in v.co))
bm.normal_update()
# v3: the stage-floor faces attached to moved foot verts (they filled the old jagged foot wedges and fold when the foot moves
# back) are deleted and the planar hole re-filled as one stage-concrete n-gon per hole (then triangulated, beauty).
FZ=lambda f: all(abs(w.co.z-132.916)<0.003 for w in f.verts)
ob0={e for e in bm.edges if e.is_boundary}
ff={g for v in moved for g in v.link_faces if FZ(g)}
nff=len(ff); bmesh.ops.delete(bm,geom=list(ff),context='FACES_ONLY')
he=[e for e in bm.edges if e.is_valid and e.is_boundary and e not in ob0]
rr=bmesh.ops.holes_fill(bm,edges=he,sides=0)
nf=rr['faces']
for f in nf: f.material_index=STG
bm.normal_update()
for f in nf:
    if f.normal.z<0: f.normal_flip()
tri=bmesh.ops.triangulate(bm,faces=nf,quad_method='BEAUTY',ngon_method='BEAUTY')
bm.normal_update()
print('JHN floor faces deleted',nff,'hole edges',len(he),'filled n-gons',len(nf),'-> tris',len(tri['faces']),'tri n.z<0.99',sum(1 for f in tri['faces'] if f.normal.z<0.99))
mv=[v for v in moved if v.is_valid]
r=bmesh.ops.remove_doubles(bm,verts=mv,dist=0.004)
bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=5e-4); bm.normal_update()
# v2: seat-stone material faces lying flat on the stage floor (z 132.916; the light sawtooth tris along the wall foot) -> stage concrete
SEAT=names.index('hn_amphi_seat_stone_blocks'); nre=0
for f in bm.faces:
    if f.is_valid and f.material_index==SEAT and f.normal.z>0.99 and all(abs(w.co.z-132.916)<0.003 for w in f.verts):
        f.material_index=STG; nre+=1
print('JHN seat-material floor faces -> stage concrete',nre)
c1=counts(); print('JHN moved',len(moved),'stage verts squashed',nstg[0],'corner verts added',ncorner[0],'reverted/partial',rev,'faces_lost_to_merge',c0['faces']-len(bm.faces)); print('JHN after',c1)
if os.environ.get('DRY')=='1': bm.free(); raise SystemExit
bm.to_mesh(me); bm.free(); me.update()
sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
os.environ['MAXA']='0'; os.environ['MAXH']='0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/jc/jc_corner_cleanup.py',run_name='__main__')
for k,v in sv.items():
    if v is not None: os.environ[k]=v
ob['jh_notch_rect']=f'2026-10-26 session jh: aisle-foot notch in the stage-front wall squared up ({len(moved)} verts moved, {rev} reverted); counts {c0} -> {c1}'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JHN WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JHN SAVED')

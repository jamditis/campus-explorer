# Session je (2026-10-26 ~2:45 AM ET): GENERIC rebuild of the amphitheater aisle-step / cheek corners
# (Kasser_amphitheater_bowl_hl, MAIN). Generalises jd's one-off front-row fix to every aisle.
# Problem: where an aisle half-step riser (vertical plane s = s_r in ip/iz's aisle frame) meets the bench cheek
# (vertical plane |d| = AW/2), the corner vertex (s_r, AW/2, z_top) never existed, so one tilted n-gon bridged the step
# riser, the cheek and the upper tread (iy custom-normal "wedges", jd's row-3-left overhang / row-2-right faces).
# Fix per bad face F (aisle side only: every vert |d| <= AW/2 + 1.5 cm, >= 1 vert on the cheek line, >= 1 interior vert):
#  s_r = min s of F's interior verts (|d| < AW/2 - 1 cm), z_top = max z of interior verts.
#  (a) interior verts with z within 3 cm of z_top and s > s_r + 1 cm are snapped back to s = s_r (straight riser top edge;
#      z kept, so the upper tread stays flat).
#  (b) a new vertex N = (s_r, +-AW/2, z_top) on the cheek line; F is replaced by a fan of triangles around N
#      (each lands on the riser plane, the cheek plane or the tread plane), attrs/material copied from F, wedge flag 0.
# Bad = non-chamfer stone face touching the cheek line with |n_d| > 0.3 and (n.z > 0.15 or n.z < -0.05), or iy_wedge = 1.
# Then the established chain: jc_corner_cleanup with MAXA=MAXH=0 (iy_wedge_normals -> iz_block_jitter -> jc_riser_uv
# -> flat normals). Env DRY=1 stats, SAVE=1, OUTB=copy. Revert = backup montclair_state_pre_20261026je.blend.
import bpy, bmesh, math, os, runpy
from mathutils import Vector as V
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SKIP={names.index(n) for n in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete')}
if me.has_custom_normals:
    try: me.free_normals_split()
    except Exception: pass
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); WL=bm.faces.layers.int.get('iy_wedge')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
def to_xy(ai,s,d):
    a=ATH[ai]; return CX+s*math.cos(a)-d*math.sin(a), CY+s*math.sin(a)+d*math.cos(a)
def isbad(f,ai):
    if f.material_index in SKIP or f[CH]: return False
    a=ATH[ai]; n=f.normal; nd=-n.x*math.sin(a)+n.y*math.cos(a)
    return (WL and f[WL]) or (abs(nd)>0.3 and (n.z>0.15 or n.z<-0.05))
def stats():
    bm.normal_update()
    down=sum(1 for f in bm.faces if f.normal.z<-0.05 and f.material_index not in SKIP)
    return down, sum(1 for e in bm.edges if len(e.link_faces)>2), len(bm.faces)
def count_bad():
    c=0
    for f in bm.faces:
        if f.material_index in SKIP: continue
        cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(cc,k)[1])-H))
        if fr(cc,ai)[0]<=0: continue
        ds=[fr(v.co,ai)[1] for v in f.verts]
        if any(abs(abs(d)-H)<0.01 for d in ds) and any(abs(d)<H-0.01 for d in ds) and all(abs(d)<=H+0.015 for d in ds) and isbad(f,ai): c+=1
    return c
d0,nm0,f0=stats(); b0=count_bad(); bd0=sum(1 for e in bm.edges if e.is_boundary); print('JE boundary before',bd0); print('JE before: bad',b0,'down',d0,'edges>2',nm0,'faces',f0)
snapped=0; made=0; done=0; flips=0; skipped=0; nofull=0; allnew=[]; failed=0; merged2=0
RIS=names.index('hn_amphi_riser_coursed_stone')
def one_pass(PASS):
    global snapped,made,done,skipped,nofull,failed,merged2
    cands=[]
    for f in bm.faces:
        if f.material_index in SKIP: continue
        cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(cc,k)[1])-H))
        if fr(cc,ai)[0]<=0: continue
        sd=[fr(v.co,ai) for v in f.verts]
        if not any(abs(abs(d)-H)<0.01 for s,d in sd): continue
        if not all(abs(d)<=H+0.015 for s,d in sd): continue
        inner=[(v,s,d) for v,(s,d) in zip(f.verts,sd) if abs(d)<H-0.01]
        if not inner or not isbad(f,ai): continue
        cands.append((f,ai))
    print('JE candidates',len(cands))
    RIS=names.index('hn_amphi_riser_coursed_stone')
    for f,ai in cands:
        if not f.is_valid: continue
        sd=[fr(v.co,ai) for v in f.verts]
        inner=[(v,s,d) for v,(s,d) in zip(f.verts,sd) if abs(d)<H-0.01]
        a_=ATH[ai]; ca,sa=math.cos(a_),math.sin(a_)
        s_r=None
        for e in f.edges:
            for g in e.link_faces:
                if g is f or g.material_index!=RIS: continue
                n=g.normal; ns=n.x*ca+n.y*sa
                if ns<-0.9 and abs(n.z)<0.1:
                    gs=[fr(v.co,ai) for v in g.verts]
                    if all(abs(d)<H+0.005 for s_,d in gs):
                        s_r=sum(s_ for s_,d in gs)/len(gs); break
            if s_r is not None: break
        if s_r is None: s_r=min(s for v,s,d in inner); nofull+=1
        sign=math.copysign(1,sum(d for s,d in sd))
        if PASS==2:   # stray cheek vert at the same level < 8 cm from another cheek vert of this face -> merge (keep the one nearer s_r)
            ch=[(v,s_,d) for v,(s_,d) in zip(f.verts,sd) if abs(d)>=H-0.01]
            mg=None
            for i in range(len(ch)):
                for j in range(len(ch)):
                    u,su,du=ch[i]; w,sw,dw=ch[j]
                    if i!=j and abs(u.co.z-w.co.z)<0.005 and 0.003<abs(su-sw)<0.08 and abs(su-s_r)>abs(sw-s_r): mg=(u,w)
            if mg:
                bmesh.ops.pointmerge(bm,verts=[mg[0],mg[1]],merge_co=mg[1].co.copy()); merged2+=1
                continue
        moved=[]
        for v,s,d in inner:
            if abs(s-s_r)>0.005 and abs(s-s_r)<0.25:
                moved.append((v,v.co.copy())); x,y=to_xy(ai,s_r,d); v.co.x,v.co.y=x,y
        z_top=max(v.co.z for v,s,d in inner)
        z_bot=min(v.co.z for v,s,d in inner)
        a_=ATH[ai]; ca,sa=math.cos(a_),math.sin(a_)
        def fan(Nco):
            vs=list(f.verts); tris=[]
            for i in range(len(vs)):
                a,b=vs[i],vs[(i+1)%len(vs)]
                if (a.co-Nco).length<1e-4 or (b.co-Nco).length<1e-4: continue
                tris.append((a,b))
            return tris
        def score(Nco,tris):
            pen=0.0
            for a,b in tris:
                cr=(a.co-Nco).cross(b.co-Nco); A=cr.length/2
                if A<1e-7: continue
                n=cr.normalized(); ns=n.x*ca+n.y*sa; nd=-n.x*sa+n.y*ca
                if n.z<-0.05: pen+=3*A
                elif n.z>0.97: pass
                elif abs(n.z)<0.08:
                    if ns>0.5 or nd*sign>0.5: pen+=3*A   # vertical but facing up-aisle / into the bench = fold
                else: pen+=A
            return pen
        f0n=f.normal; A0=f.calc_area()
        best=None
        for lim in (0.05,0.2):
            csn=[]
            for v,(s_,d) in zip(f.verts,sd):   # cheek verts near the riser plane at riser-top level join it (tread front corner)
                if abs(d)>=H-0.01 and 0.003<abs(s_-s_r)<lim and abs(v.co.z-z_top)<0.025:
                    csn.append((v,v.co.copy())); x,y=to_xy(ai,s_r,d); v.co.x,v.co.y=x,y
            for zc in (z_top,z_bot):
                x,y=to_xy(ai,s_r,sign*H); Nco=V((x,y,zc)); tr=fan(Nco); sc=score(Nco,tr)
                if best is None or sc<best[0]-1e-6: best=(sc,Nco,tr,lim,[(v,v.co.copy(),o) for v,o in csn])
            for v,co in csn: v.co=co
        for v,co,o in best[4]: v.co=co
        cmoved=best[4]
        if os.environ.get('VERB')=='2': print('JEV2 c',[round(x,3) for x in f.calc_center_median()],'A0',round(A0*1e4,1),'best',round(best[0]*1e4,1),'z',round(best[1].z,3),'s_r',round(s_r,3),'moved',len(moved))
        if best[0]>=0.5*A0:
            for v,co in moved: v.co=co
            for v,co,o in cmoved: v.co=o
            skipped+=1; continue
        snapped+=len(moved)+len(cmoved)
        N=bm.verts.new(best[1]); z_top=best[1].z; new=[]
        for a,b in best[2]:
            try: g=bm.faces.new((a,b,N),f)
            except ValueError: failed+=1; continue
            new.append(g)
        if WL:
            for g in new: g[WL]=0
        bm.faces.remove(f); made+=len(new); done+=1; allnew.extend(new)
        for g in new:
            g.normal_update()
            if g.normal.z<-0.05 and os.environ.get('VERB')=='1':
                print('JEV down tri face',done,'c',[round(x,3) for x in g.calc_center_median()],'n',[round(x,2) for x in g.normal],'A cm2',round(g.calc_area()*1e4,1),'z_top',round(z_top,3),'pts',[(round(fr(v.co,ai)[0],3),round(abs(fr(v.co,ai)[1]),3),round(v.co.z,3)) for v in g.verts])

one_pass(1)
bm.normal_update(); print('JE after pass1 bad',count_bad())
one_pass(2)
bm.normal_update(); print('JE pass2 stray cheek merges',merged2,'bad',count_bad())
one_pass(3)
bm.normal_update()
tiny=0
for it in range(3):
    dn=[g for g in allnew if g.is_valid and g.normal.z<-0.05 and g.calc_area()<6e-4]
    if not dn: break
    used=set()
    for g in dn:
        if not g.is_valid or any(v in used for v in g.verts): continue
        vs=list(g.verts); used.update(vs); c=sum((v.co for v in vs),V((0,0,0)))/len(vs)
        bmesh.ops.pointmerge(bm,verts=vs,merge_co=c); tiny+=1
    bm.normal_update()
print('JE tiny folded tris collapsed',tiny)
r=bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=2e-4)
lone=[v for v in bm.verts if not v.link_faces]
if lone: bmesh.ops.delete(bm,geom=lone,context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=[g for g in bm.faces if g.is_valid]) if os.environ.get('RECALC')=='1' else None
d1,nm1,f1=stats(); b1=count_bad()
bd=sum(1 for e in bm.edges if e.is_boundary)
print('JE face.new failures',failed); print('JE skipped',skipped,'no full riser neighbour',nofull); print('JE rebuilt',done,'faces into',made,'tris; snapped',snapped,'verts; bad',b0,'->',b1,'down',d0,'->',d1,'edges>2',nm0,'->',nm1,'faces',f0,'->',f1,'boundary edges',bd)
if os.environ.get('DRY')=='1': bm.free(); raise SystemExit
bm.to_mesh(me); bm.free(); me.update()
sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
os.environ['MAXA']='0'; os.environ['MAXH']='0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/jc/jc_corner_cleanup.py',run_name='__main__')
for k,v in sv.items():
    if v is not None: os.environ[k]=v
ob['je_cheek_corners']=f'2026-10-26 session je: {done} aisle-step/cheek corner faces rebuilt as fans around a new corner vertex ({snapped} riser-top verts snapped); bad {b0}->{b1}; chain re-run'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JE WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JE SAVED')

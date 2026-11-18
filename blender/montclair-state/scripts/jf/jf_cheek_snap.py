# Session jf (2026-10-26 ~3:30 AM ET): finish the last aisle-step/cheek corner faces je left (west aisle ai 1, s 8.7-29.7).
# Diagnosis (jf_diag.py): each remaining bad face is a near-vertical cheek face (on |d| = AW/2) pulled off-plane by
#  (A) a bench-end corner vertex left 4.5-7.5 cm INSIDE the cheek line (|d| 0.576-0.606), or
#  (B) one jb chamfer-inset vertex (|d| ~0.633, 1.8 cm inside) sharing the cheek n-gon.
# Fix: (A) snap those verts outward onto the cheek line (s and z kept, so treads stay flat and step risers stay in their
#  planes); revert a snap if any linked face turns down-facing. (B) split the face between the two cheek-line neighbours of
#  the inset vert (connect_verts) so the cheek part is planar and the inset vert sits in a tiny transition tri, tagged jb_chamfer.
# Then the established chain jc_corner_cleanup MAXA=MAXH=0 (iy_wedge_normals -> iz_block_jitter -> jc_riser_uv -> flat normals).
# Env DRY=1 stats only, SAVE=1, OUTB=copy path. Revert = backup montclair_state_pre_20261026jf.blend.
import bpy, bmesh, math, os, runpy
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
def bad_faces():
    out=[]
    for f in bm.faces:
        if f.material_index in SKIP: continue
        cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(cc,k)[1])-H))
        if fr(cc,ai)[0]<=0: continue
        ds=[fr(v.co,ai)[1] for v in f.verts]
        if any(abs(abs(d)-H)<0.01 for d in ds) and any(abs(d)<H-0.01 for d in ds) and all(abs(d)<=H+0.015 for d in ds) and isbad(f,ai): out.append((f,ai))
    return out
def ndown(): return sum(1 for f in bm.faces if f.normal.z<-0.05 and f.material_index not in SKIP)
b0=len(bad_faces()); d0=ndown(); f0=len(bm.faces); bd0=sum(1 for e in bm.edges if e.is_boundary)
print('JF before bad',b0,'down',d0,'faces',f0,'boundary',bd0)
snapA=0; revA=0; snapA2=0
def fbad(g,ai):
    if g.material_index in SKIP: return False
    ds=[fr(v.co,ai)[1] for v in g.verts]
    return isbad(g,ai) and any(abs(abs(d)-H)<0.025 for d in ds)
def ok(v,ai,nb0):
    for g in v.link_faces: g.normal_update()
    if any(g.normal.z<-0.05 and g.material_index not in SKIP and g.calc_area()>2e-4 for g in v.link_faces): return False
    return sum(fbad(g,ai) for g in v.link_faces) < nb0
for f,ai in bad_faces():
    if not f.is_valid: continue
    for v in list(f.verts):
        s,d=fr(v.co,ai)
        if H-0.085<abs(d)<H-0.025:
            old=v.co.copy(); nb0=sum(fbad(g,ai) for g in v.link_faces); done=False
            for tgt,lab in ((H,'A'),(H-0.018,'A2')):   # cheek line, else the jb chamfer-inset line (1.8 cm inside)
                x,y=to_xy(ai,s,math.copysign(tgt,d)); v.co.x,v.co.y=x,y
                if ok(v,ai,nb0):
                    done=True
                    if lab=='A': snapA+=1
                    else: snapA2+=1
                    break
                v.co=old.copy()
            if not done:
                v.co=old; revA+=1
                for g in v.link_faces: g.normal_update()
bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=2e-4)
lone=[v for v in bm.verts if not v.link_faces]
if lone: bmesh.ops.delete(bm,geom=lone,context='VERTS')
print('JF A2 (to chamfer-inset line)',snapA2)
bm.normal_update(); b1=len(bad_faces()); print('JF after A: snapped',snapA,'reverted',revA,'bad',b1)
splitB=0; tagB=0
for f,ai in bad_faces():
    if not f.is_valid: continue
    vs=list(f.verts); sd=[fr(v.co,ai) for v in vs]
    ins=[i for i,(s_,d) in enumerate(sd) if H-0.025<=abs(d)<H-0.01]
    n_=len(vs)
    if not ins or len(ins)>2 or n_<4: continue
    if len(ins)==2:
        i0,i1=sorted(ins)
        if i1-i0==1: run=(i0,i1)
        elif i0==0 and i1==n_-1: run=(i1,i0)
        else: continue
    else: run=(ins[0],ins[0])
    a,b=vs[run[0]-1],vs[(run[1]+1)%n_]; i=ins[0]
    if not all(abs(abs(fr(v.co,ai)[1])-H)<0.005 for v in (a,b)): continue
    if bm.edges.get((a,b)): continue
    r=bmesh.ops.connect_verts(bm,verts=[a,b])
    if not r['edges']: continue
    splitB+=1
    e=r['edges'][0]
    for g in e.link_faces:
        g.normal_update()
        if any(vs[j] in g.verts for j in ins):
            g[CH]=1; tagB+=1
            if WL: g[WL]=0
bm.normal_update()
b2=len(bad_faces()); d2=ndown(); f2=len(bm.faces); bd2=sum(1 for e in bm.edges if e.is_boundary); nm=sum(1 for e in bm.edges if len(e.link_faces)>2)
print('JF after B: split',splitB,'transition tris tagged',tagB,'bad',b0,'->',b2,'down',d0,'->',d2,'faces',f0,'->',f2,'boundary',bd0,'->',bd2,'edges>2',nm)
for f,ai in bad_faces(): print('JF left',[round(x,2) for x in f.calc_center_median()],'A cm2',round(f.calc_area()*1e4,1),'n',[round(x,2) for x in f.normal],[(round(fr(v.co,ai)[0],3),round(fr(v.co,ai)[1],3),round(v.co.z,3)) for v in f.verts])
# (C) aisle half-step "tent" wedges (iy_wedge faces inside the aisle, n.z ~0.6): one tread-level vertex v* sits 15-20 cm
#  off the step-riser plane s = s_r and the face bridges tread and riser. Split between v*'s two loop neighbours (both on the
#  riser line at v*'s height): the v* tri is flat tread (takes the material of an up-facing face at v*), the rest is the vertical riser.
splitC=0
def wedge_cands():
    out=[]
    for f in bm.faces:
        if f.material_index in SKIP or f[CH]: continue
        if not ((WL and f[WL]) or 0.12<f.normal.z<0.95): continue
        cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(fr(cc,k)[1]))
        s_,d_=fr(cc,ai)
        if s_<=0 or abs(d_)>H-0.005: continue
        out.append((f,ai))
    return out
for f,ai in wedge_cands():
    if not f.is_valid: continue
    vs=list(f.verts); n_=len(vs)
    if n_<4: continue
    ss=[fr(v.co,ai)[0] for v in vs]; med=sorted(ss)[n_//2]
    k=max(range(n_),key=lambda i:abs(ss[i]-med))
    if not 0.05<abs(ss[k]-med)<0.3: continue
    a,b=vs[k-1],vs[(k+1)%n_]; vk=vs[k]
    if not all(abs(fr(v.co,ai)[0]-med)<0.025 and abs(v.co.z-vk.co.z)<0.012 for v in (a,b)): continue
    if bm.edges.get((a,b)): continue
    up=[g for g in vk.link_faces if g is not f and g.normal.z>0.97]
    r=bmesh.ops.connect_verts(bm,verts=[a,b])
    if not r['edges']: continue
    splitC+=1
    for g in r['edges'][0].link_faces:
        g.normal_update()
        if WL: g[WL]=0
        if vk in g.verts and up: g.material_index=up[0].material_index
bm.normal_update()
left=[(round(fr(f.calc_center_median(),ai)[0],2),round(fr(f.calc_center_median(),ai)[1],2),round(f.normal.z,2),round(f.calc_area()*1e4)) for f,ai in wedge_cands()]
print('JF C: tent wedges split',splitC,'tilted/wedge faces left inside aisles',len(left),'down',ndown(),'boundary',sum(1 for e in bm.edges if e.is_boundary),'edges>2',sum(1 for e in bm.edges if len(e.link_faces)>2))
for x in sorted(left): print('JF C left',x)
if os.environ.get('DRY')=='1': bm.free(); raise SystemExit
bm.to_mesh(me); bm.free(); me.update()
sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','DRY')}
os.environ['MAXA']='0'; os.environ['MAXH']='0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/jc/jc_corner_cleanup.py',run_name='__main__')
for k,v in sv.items():
    if v is not None: os.environ[k]=v
ob['jf_cheek_snap']=f'2026-10-26 session jf: {snapA} bench-end verts snapped onto the cheek line, {splitB} cheek faces split off chamfer transition tris; bad {b0}->{b2}; chain re-run'
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JF WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JF SAVED')

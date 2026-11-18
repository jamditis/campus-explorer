# Session ja (2026-10-25 ~10:25 PM ET): square the aisle half-step tread edges between iz's straight cheek lines.
# Problem (iz): inside the aisle band the half-step treads are still on the 8 cm grid, so each step edge is a staircase in plan;
# the one-cell transition faces (verts on two half-levels) show as pale triangular facets.
# Fix: aisle verts (|d| <= AW/2 + 1 cm, s > 0; same axes as iz) are grouped per (aisle, half-level). For each step between
# half-levels lo/hi, all verts of the transition faces are moved ALONG the aisle axis (d kept, so cheek-line verts stay on
# the cheek plane) onto one line s = s_edge (median of those verts' s) = a straight edge perpendicular to the aisle; the
# transition faces collapse into a vertical riser plane; zero-area faces dissolved. Moves > 0.16 m or verts claimed by two steps
# are skipped. Original xy stored in object prop ja_orig (REVERT=1 restores xy; use the backup for a full revert).
# Order: ... -> iz_aisle_cheeks -> iy_wedge_normals -> iz_block_jitter -> ja_aisle_treads -> iy_wedge_normals -> iz_block_jitter.
import bpy, bmesh, numpy as np, os, math, json
SRC='/workspace/nj-scenes/montclair-state/scripts/ip/ip_amphi_build.py'
L=open(SRC).read().split('\n'); code='\n'.join(L[10:42]+L[56:69])
os.environ['RES']='0.08'; g={}; exec(code,g)
CX,CY,AW,ATH=g['CX'],g['CY'],g['AW'],g['AISLE_TH']; Z_STAGE=g['Z_STAGE']; RISER=g['RISER']; H=RISER/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
RIS=names.index('hn_amphi_riser_coursed_stone'); BASE=names.index('hn_amphi_base_fieldstone'); STAGE=names.index('io_amphi_stage_concrete')
if os.environ.get('REVERT')=='1':
    d=json.loads(ob['ja_orig'])
    for i,(x,y) in d.items(): me.vertices[int(i)].co.x=x; me.vertices[int(i)].co.y=y
    me.update(); print('JA REVERTED xy')
else:
    if me.has_custom_normals:
        try: me.free_normals_split()
        except Exception: pass
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    def dinfo(co):
        best=None
        for ai,a in enumerate(ATH):
            dx,dy=co.x-CX,co.y-CY; s=dx*math.cos(a)+dy*math.sin(a); d=-dx*math.sin(a)+dy*math.cos(a)
            if best is None or abs(d)<abs(best[2]): best=(ai,s,d)
        return best
    info={v.index:dinfo(v.co) for v in bm.verts}
    skip=set(v.index for v in bm.verts if v.is_boundary or any(f.material_index in (BASE,STAGE) for f in v.link_faces))
    inA={i:(abs(d)<=AW/2+0.01 and s>0) for i,(ai,s,d) in info.items()}
    lev={v.index:(v.co.z-Z_STAGE)/H for v in bm.verts}
    def onplane(i): return abs(abs(info[i][2])-AW/2)<0.01
    steps={}
    for f in bm.faces:
        if f.material_index in (BASE,STAGE): continue
        ids=[v.index for v in f.verts]
        if not all(inA[i] for i in ids): continue
        if all(onplane(i) for i in ids): continue   # iz cheek face
        ls=[lev[i] for i in ids]
        if max(ls)-min(ls)<0.2: continue
        lo=int(round(min(ls))); ai=info[ids[0]][0]
        steps.setdefault((ai,lo),set()).update(ids)
    owner={}; conflict=set()
    for k,ids in steps.items():
        for i in ids:
            if i in owner and owner[i]!=k: conflict.add(i)
            owner[i]=k
    proj={}; mv=[]; nstep=0
    for (ai,lo),ids in steps.items():
        ok=[i for i in ids if i not in skip and i not in conflict]
        if len(ok)<3: continue
        se=float(np.median([info[i][1] for i in ok])); a=ATH[ai]; nstep+=1
        for i in ok:
            s,d=info[i][1],info[i][2]
            if abs(s-se)>0.16: continue
            proj[i]=(CX+se*math.cos(a)-d*math.sin(a), CY+se*math.sin(a)+d*math.cos(a)); mv.append(abs(s-se))
    n0=sum(1 for f in bm.faces if f.normal.z<-0.05)
    print('JA steps',len(steps),'used',nstep,'verts moved',len(proj),'conflicts',len(conflict),'move pct50/95/max',[round(float(np.percentile(mv,q)),3) for q in (50,95,100)] if mv else None)
    if os.environ.get('DRY')!='1':
        ob['ja_orig']=json.dumps({str(i):[bm.verts[i].co.x,bm.verts[i].co.y] for i in proj})
        for i,(x,y) in proj.items(): bm.verts[i].co.x=x; bm.verts[i].co.y=y
        bm.normal_update()
        nv=0
        for k,ids in steps.items():
            pass
        for f in bm.faces:
            if f.material_index in (BASE,STAGE): continue
            if any(v.index in proj for v in f.verts) and abs(f.normal.z)<0.35 and f.calc_area()>1e-5: f.material_index=RIS; nv+=1
        nb=len(bm.faces); bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=1e-3); bm.normal_update()
        n1=sum(1 for f in bm.faces if f.normal.z<-0.05)
        print('JA vertical riser faces',nv,'removed by dissolve',nb-len(bm.faces),'down-facing before/after',n0,n1)
        bm.to_mesh(me); bm.free(); me.update(); me.set_sharp_from_angle(angle=math.radians(30))
        a=me.attributes.get('iy_wedge')
        if a: a.data.foreach_set('value',np.zeros(len(me.polygons),np.int32))
        ob['ja_aisle_treads']='2026-10-25 session ja: aisle half-step edges squared perpendicular to the aisle'
    else: bm.free()
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JA WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JA SAVED')

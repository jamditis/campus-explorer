# Session iz (2026-10-25 ~9:30 PM ET): real vertical stone cheeks where the amphitheater rows meet the aisle half-steps.
# Problem (iy): on the 8 cm grid the aisle boundary is a staircase; the one-cell transition faces between aisle half-step verts
# and row verts form a jagged sawtooth that casts black notch shadows by the handrail.
# Fix (geometry): the aisle band is |r*sin(theta-a)| < AW/2 about ip's aisle axes (same CX/CY/AISLE_TH, recomputed from ip's
# code at RES=0.08). Ring verts = aisle-side verts of mixed faces (inner ring) + row-side verts of mixed faces (outer ring), within
# +-0.16 m of the edge line and not on the outline/skirt. Both rings are projected perpendicular onto the straight edge line
# |d| = AW/2 (s along the aisle kept). Interior aisle verts all have |d| < AW/2 and row verts > AW/2, so nothing folds; every mixed
# face collapses onto the vertical plane = a true vertical cheek (riser coursed stone). Zero-area faces dissolved.
# iy's custom wedge normals are cleared first (iy_wedge_normals.py + iy_block_len.py are re-run after this to re-tag / re-derive UVs).
# Order: ip -> ... -> ix -> iy_* -> iz_aisle_cheeks -> iy_wedge_normals -> iy_block_len. Env DRY=1 stats only. Original vertex
# positions stored in object prop iz_orig (json idx->xy) so REVERT=1 can restore xy (topology is unchanged except degenerate dissolve).
import bpy, bmesh, numpy as np, os, math, json
SRC='/workspace/nj-scenes/montclair-state/scripts/ip/ip_amphi_build.py'
L=open(SRC).read().split('\n'); code='\n'.join(L[10:42]+L[56:69])
os.environ['RES']='0.08'; g={}; exec(code,g)
CX,CY,AW,ATH=g['CX'],g['CY'],g['AW'],g['AISLE_TH']; Z_STAGE=g['Z_STAGE']; RISER=g['RISER']
print('IZ centre',round(CX,3),round(CY,3),'AW',AW,'axes',[round(a,4) for a in ATH])
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
RIS=names.index('hn_amphi_riser_coursed_stone'); BASE=names.index('hn_amphi_base_fieldstone'); STAGE=names.index('io_amphi_stage_concrete')
if os.environ.get('REVERT')=='1':
    d=json.loads(ob['iz_orig'])
    for i,(x,y) in d.items(): me.vertices[int(i)].co.x=x; me.vertices[int(i)].co.y=y
    me.update(); print('IZ REVERTED xy (materials not restored)')
else:
    if me.has_custom_normals:
        bpy.context.view_layer.objects.active=ob
        try: me.free_normals_split()
        except Exception: bpy.ops.mesh.customdata_custom_splitnormals_clear()
    print('IZ custom normals now',me.has_custom_normals)
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    def dinfo(co):
        best=None
        for ai,a in enumerate(ATH):
            dx,dy=co.x-CX,co.y-CY; s=dx*math.cos(a)+dy*math.sin(a); d=-dx*math.sin(a)+dy*math.cos(a)
            if best is None or abs(d)<abs(best[2]): best=(ai,s,d)
        return best
    info={v.index:dinfo(v.co) for v in bm.verts}
    skip=set(v.index for v in bm.verts if v.is_boundary or any(f.material_index in (BASE,STAGE) for f in v.link_faces))
    inA={i:(abs(d)<AW/2 and s>0) for i,(ai,s,d) in info.items()}
    ring=set(); mixed=[]
    for f in bm.faces:
        if f.material_index in (BASE,STAGE): continue
        fl=[inA[v.index] for v in f.verts]
        if any(fl) and not all(fl):
            mixed.append(f)
            for v in f.verts: ring.add(v.index)
    proj={}
    for i in ring:
        if i in skip: continue
        ai,s,d=info[i]
        if abs(abs(d)-AW/2)>0.16: continue
        a=ATH[ai]; dd=math.copysign(AW/2,d)
        proj[i]=(CX+s*math.cos(a)-dd*math.sin(a), CY+s*math.sin(a)+dd*math.cos(a))
    mv=np.array([math.hypot(proj[i][0]-bm.verts[i].co.x,proj[i][1]-bm.verts[i].co.y) for i in proj])
    print('IZ mixed faces',len(mixed),'ring verts',len(ring),'projected',len(proj),'move pct50/95/max',[round(float(np.percentile(mv,q)),3) for q in (50,95,100)])
    if os.environ.get('DRY')!='1':
        ob['iz_orig']=json.dumps({str(i):[bm.verts[i].co.x,bm.verts[i].co.y] for i in proj})
        for i,(x,y) in proj.items(): bm.verts[i].co.x=x; bm.verts[i].co.y=y
        bm.normal_update()
        nv=0
        for f in mixed:
            if f.is_valid and abs(f.normal.z)<0.35 and f.calc_area()>1e-5: f.material_index=RIS; nv+=1
        nb=len(bm.faces); bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=1e-3)
        print('IZ vertical cheek faces',nv,'faces removed by dissolve_degenerate',nb-len(bm.faces))
        bm.to_mesh(me); bm.free(); me.update(); me.set_sharp_from_angle(angle=math.radians(30))
        n=np.empty(len(me.polygons)*3); me.polygons.foreach_get('normal',n); n=n.reshape(-1,3)
        a=me.attributes.get('iy_wedge')
        if a: a.data.foreach_set('value',np.zeros(len(me.polygons),np.int32))
        ob['iz_aisle_cheeks']='2026-10-25 session iz: aisle edges projected onto straight lines, vertical stone cheeks'
        print('IZ down-facing faces',int((n[:,2]<-0.05).sum()))
    else: bm.free()

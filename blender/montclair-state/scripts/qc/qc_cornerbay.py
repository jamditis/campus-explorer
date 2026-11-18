# qc (Nov 2 2026): the 15 Calcia wall cells that qb_corner kept (they still hold a FULL-WIDTH shader-painted window).
# Probe (data/qc/inspect.log, probe.log): only ONE of them is a real uncut bay - face at u 89.55-91.04 (west face, column 37,
# both storeys; pr/ps skipped it because the slot starts exactly on the building corner). The other 14 are slivers/stubs of
# painted glass: 0.11-0.12 m strips above ps openings (11), a 0.06 m strip under one (1), and two 0.46-0.75 m stub windows
# under a lower roof line (2). -> the real bay gets 2 recessed openings in the pr/ps style (frame 5 cm bronze + transom +
# precast sill, tan reveals 0.22 m, tinted glass set back 0.12 m, dark interior box 0.6 m), inset 0.12 m from the corner so the
# jamb does not overhang the corner; ALL 15 cells (and the cut remainder) use slot 1 = QB_Calcia_brick_no_shader_windows_UNVERIFIED.
# Original wall mesh kept as fake-user mesh 'QC_backup_Calcia_walls'; REVERT=1 restores it exactly. ALL UNVERIFIED.
import bpy, bmesh, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; ON='QC_Calcia_cornerbay_frames_reveals_glass_UNVERIFIED'; BK='QC_backup_Calcia_walls'
w=bpy.data.objects['Calcia Hall walls']; me=w.data
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m2=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m2); print('REVERTED_QC_OBJ')
if BK in bpy.data.meshes:
    bk=bpy.data.meshes[BK]; bm=bmesh.new(); bm.from_mesh(bk); bm.to_mesh(me); bm.free(); me.update()
    bpy.data.meshes.remove(bk); print('REVERTED_QC_WALLS V',len(me.vertices))
    if 'UNVERIFIED_qc' in w: del w['UNVERIFIED_qc']
if not REV:
    exec(open('scripts/qc/qc_find.py').read(),globals())
    FS,WT=qc_find(); assert len(FS)==15,len(FS)
    assert me.materials[1].name=='QB_Calcia_brick_no_shader_windows_UNVERIFIED'
    bk=me.copy(); bk.name=BK; bk.use_fake_user=True
    mw=w.matrix_world; imw=mw.inverted()
    CUT=[]   # (face dict, u0,u1,v0,v1)
    for F in FS:
        for k in F['cols']:
            u0=2.4*k+0.75; u1=u0+0.9
            if u0-F['umin']<0.1: u0=F['umin']+0.12
            if F['umax']-u1<0.1: u1=F['umax']-0.12
            def top_at(u,UV=F['UV']):   # highest boundary crossing of the cell outline at facade-U u
                t=[]
                for a,b in zip(UV,UV[1:]+UV[:1]):
                    if (a.x-u)*(b.x-u)<=0 and abs(b.x-a.x)>1e-6: t.append(a.y+(b.y-a.y)*(u-a.x)/(b.x-a.x))
                return max(t) if t else -1e9
            ltop=min(top_at(u0-0.06+i*(u1-u0+0.12)/20) for i in range(21))
            for (js,L0,H0,lo,hi) in F['rows']:
                if H0>ltop-0.12: H0=round(ltop-0.12,3); hi=min(hi,H0)   # keep a 0.12 m head below the local wall top (ps rule)
                if lo<=L0+0.01 and hi>=H0-0.01 and F['vmax']>=H0+0.1 and F['vmin']<=L0-0.1 and u1-u0>0.6 and H0-L0>=1.0:
                    CUT.append((F,u0,u1,L0,H0))
    print('QC_CUT',[(F['idx'],round(F['res'],4),round(F['Wu'].angle(F['Wv']),4),round(a,2),round(b,2),c,d) for F,a,b,c,d in CUT])
    bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    src=bm.faces.layers.int.new('qc_src')
    for f in bm.faces: f[src]=f.index
    uvL=bm.loops.layers.uv['facade']; keep=set(F['idx'] for F in FS)
    byf={}
    for c in CUT: byf.setdefault(c[0]['idx'],[]).append(c)
    for fi,cs in byf.items():
        F=cs[0][0]; f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y)
        planes=set()
        for (_,u0,u1,v0,v1) in cs: planes|={('u',round(u0,4)),('u',round(u1,4)),('v',round(v0,4)),('v',round(v1,4))}
        for kind,val in sorted(planes):
            fs=[x for x in bm.faces if x[src]==fi]
            geom=list(fs)+list({e for x in fs for e in x.edges})+list({v for x in fs for v in x.verts})
            nn=F['Wu'].cross(F['Wv']).normalized()   # plane normals perpendicular to the iso-lines (Wu, Wv need not be orthogonal)
            if kind=='u': co=imw@f(val,F['U0'].y); no=(imw.to_3x3()@nn.cross(F['Wv'])).normalized()
            else: co=imw@f(F['U0'].x,val); no=(imw.to_3x3()@nn.cross(F['Wu'])).normalized()
            bmesh.ops.bisect_plane(bm,geom=geom,dist=0.0005,plane_co=co,plane_no=no)
    dele=[]; n1=0
    for x in bm.faces:
        if x[src] not in keep: continue
        uvs=[l[uvL].uv for l in x.loops]; uc=sum(q.x for q in uvs)/len(uvs); vc=sum(q.y for q in uvs)/len(uvs)
        if any(u0<uc<u1 and v0<vc<v1 for (F,u0,u1,v0,v1) in byf.get(x[src],[])): dele.append(x)
        else: x.material_index=1; n1+=1
    bmesh.ops.delete(bm,geom=dele,context='FACES_ONLY'); bm.faces.layers.int.remove(src)
    bm.to_mesh(me); bm.free(); me.update(); print('QC_cut cells',len(dele),'slot1 cells',n1,'V',len(me.vertices))
    bm=bmesh.new()
    def quad(a,b,c,d,mi): bm.faces.new([bm.verts.new(a),bm.verts.new(b),bm.verts.new(c),bm.verts.new(d)]).material_index=mi
    def box(c,ex,ey,ez,mi):
        vs=[bm.verts.new(c+ex*sx+ey*sy+ez*sz) for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)]
        for q in [(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]: bm.faces.new([vs[i] for i in q]).material_index=mi
    for (F,u0,u1,v0,v1) in CUT:
        n=F['n']; f=lambda u,v: F['P0']+F['Wu']*(u-F['U0'].x)+F['Wv']*(v-F['U0'].y); eu=F['Wu'].normalized(); ev=F['Wv'].normalized()
        A=f(u0,v0); B=f(u1,v0); C=f(u1,v1); D=f(u0,v1); dr=-n*0.22; dg=-n*0.12; db=-n*0.6
        for p,q in ((A,B),(B,C),(C,D),(D,A)): quad(p,q,q+dr,p+dr,0)
        quad(A+dg,B+dg,C+dg,D+dg,1); quad(A+db,B+db,C+db,D+db,2)
        for p,q in ((A+dr,B+dr),(B+dr,C+dr),(C+dr,D+dr),(D+dr,A+dr)): quad(p,q,q+(db-dr),p+(db-dr),2)
        def fr(ua,ub,va,vb,d0,d1,mi):   # box from d0 to d1 proud of the wall plane (d0>0: never coplanar with the wall)
            cc=f((ua+ub)/2,(va+vb)/2)+n*((d0+d1)/2); box(cc,eu*(abs(ub-ua)/2),ev*(abs(vb-va)/2),n*((d1-d0)/2),mi)
        fw=0.05
        fr(u0-fw,u0,v0-fw,v1+fw,0.002,0.05,3); fr(u1,u1+fw,v0-fw,v1+fw,0.002,0.05,3)
        fr(u0,u1,v1,v1+fw,0.002,0.05,3); fr(u0,u1,v0-fw,v0,0.002,0.05,3)
        tv=v0+(v1-v0)/3; fr(u0,u1,tv-0.02,tv+0.02,0.003,0.03,3)
        fr(u0-0.08,u1+0.08,v0-fw-0.07,v0-fw,0.002,0.06,4)
    m2=bpy.data.meshes.new(ON); bm.to_mesh(m2); bm.free()
    for nm in ('PS_precast_reveal_tan_UNVERIFIED','PS_slot_glass_tinted_UNVERIFIED','PS_slot_interior_dark_UNVERIFIED','PE_Dickson_coping_dark_bronze_UNVERIFIED'):
        m2.materials.append(bpy.data.materials[nm])
    pr=bpy.data.objects['PR_Calcia_slot_surrounds_UNVERIFIED'].data; m2.materials.append(pr.materials[1])
    o=bpy.data.objects.new(ON,m2); w.users_collection[0].objects.link(o)
    w['UNVERIFIED_qc']='qc (Nov 2 2026): %d real corner-bay openings cut; %d qb-kept cells -> no-window shader'%(len(CUT),n1)
    print('QC_CORNERBAY openings',len(CUT),'col',w.users_collection[0].name,'polys',len(m2.polygons))

# qf (Nov 2 2026): CCIS restyle in MAIN to the photo refs/web/20261102/CCIS_building.jpg (+ montclarion_ccis_2023.jpg entrance).
# Photo-based (kind): red frames/mullions, red spandrels in tall bays, round-headed 3rd-floor windows, 2-storey arch centre bay,
# white piers between recessed bays, tan ashlar plinth, belt course, dark-red eave brackets, red entrance doors + cornice canopy w/ lettering.
# Positions/sizes/counts APPROXIMATE (photo face assumed = west, College Hall-side tower to the right). Unphotographed faces UNVERIFIED.
# Method: per wall run a 0.28 m stucco skin slab (exact boolean openings -> real reveals), glass 0.20 m behind the skin face.
# qe window/entrance object hidden (not deleted); qe cover-wall windows kept as a recoloured copy. REVERT=1 -> exact qe state.
import bpy, bmesh, os, math, json
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CN='Center for Computing and Information Science'
QEO='QE_CCIS_window_units_entrances_UNVERIFIED'
MN={'red':'QF_CCIS_red_frame_photo','spand':'QF_CCIS_red_spandrel_photo','brk':'QF_CCIS_bracket_darkred_photo','stone':'QF_CCIS_plinth_tan_ashlar_photo','let':'QF_CCIS_lettering_black'}
def rm():
    for o in [o for o in bpy.data.objects if o.get('qf')]:
        d=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if d is not None and d.users==0:
            for coll in (bpy.data.meshes,bpy.data.cameras,bpy.data.curves):
                if d.name in coll and coll[d.name]==d: coll.remove(d); break
    for o in bpy.data.objects:
        if o.get('qf_slot') is not None:
            sl=o.material_slots[o['qf_slot']]; sl.material=None; sl.link='DATA'; del o['qf_slot']
    q=bpy.data.objects.get(QEO)
    if q and q.get('qf_hidden'): q.hide_render=False; q.hide_viewport=False; del q['qf_hidden']
    for m in MN.values():
        if m in bpy.data.materials and bpy.data.materials[m].users==0: bpy.data.materials.remove(bpy.data.materials[m])
    for me in [m for m in bpy.data.meshes if m.users==0 and m.name.startswith('QF_')]: bpy.data.meshes.remove(me)
    for cu in [c for c in bpy.data.curves if c.users==0 and c.name.startswith('QF_')]: bpy.data.curves.remove(cu)
rm()
if REV: print('QF_CCIS reverted')
else:
    col=bpy.data.collections[CN]
    def mat(k,rgb,rough=0.5):
        m=bpy.data.materials.new(MN[k]); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; return m
    red=mat('red',(0.30,0.035,0.03),0.45); spd=mat('spand',(0.27,0.04,0.035),0.6); brk=mat('brk',(0.20,0.03,0.025),0.55)
    stone=mat('stone',(0.50,0.46,0.38),0.85); let=mat('let',(0.02,0.02,0.02),0.5)
    stucco=bpy.data.materials['QE_CCIS_stucco_no_shader_windows_UNVERIFIED']
    glassM=bpy.data.materials['PS_slot_glass_tinted_UNVERIFIED']; darkM=bpy.data.materials['PS_slot_interior_dark_UNVERIFIED']; sillM=bpy.data.materials['North_Feliciano_sill_tan']
    poly=[Vector((x,y)) for x,y in json.load(open('north/data/day_heroes/day7_geom.json'))['buildings'][CN]['poly_m']][:-1]
    NP=len(poly); area=sum(poly[i].x*poly[(i+1)%NP].y-poly[(i+1)%NP].x*poly[i].y for i in range(NP))/2
    W=bpy.data.objects[CN+' walls']; R=bpy.data.objects[CN+' roof (LiDAR)']
    segs=[]
    for p in W.data.polygons:
        if abs(p.normal.z)>0.2: continue
        vs=[W.matrix_world@W.data.vertices[i].co for i in p.vertices]
        segs.append((Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs))),min(v.z for v in vs),max(v.z for v in vs)))
    dg=bpy.context.evaluated_depsgraph_get(); Re=R.evaluated_get(dg); Rinv=R.matrix_world.inverted()
    def roof_at(xy):
        o=Rinv@Vector((xy.x,xy.y,200)); d=(Rinv.to_3x3()@Vector((0,0,-1))).normalized()
        ok,loc,n,i=Re.ray_cast(o,d); return (R.matrix_world@loc).z if ok else None
    def wall_at(xy):
        b=[s for s in segs if (s[0]-xy).length<1.2]
        return (min(s[1] for s in b),max(s[2] for s in b)) if b else None
    P=0.28; Z=Vector((0,0,1))
    bmS=bmesh.new(); bmC=bmesh.new(); bmW=bmesh.new()   # skin slabs, cutters, window parts
    def box(bm,c,ax,ay,az,hx,hy,hz,mi):
        vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+az*sz*hz) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
        for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
            bm.faces.new([vs[k] for k in f]).material_index=mi
    def outline(w,zb,zt,arch,segn=16):
        # 2D (u,z) outline of an opening centred at u=0
        if not arch: return [(-w/2,zb),(w/2,zb),(w/2,zt),(-w/2,zt)]
        r=w/2; zs=zt-r; pts=[(-w/2,zb),(w/2,zb)]
        for k in range(segn+1):
            a=math.pi*k/segn; pts.append((r*math.cos(a),zs+r*math.sin(a)))
        return pts
    def prism(bm,pc,t,n,pts,o0,o1,mi):
        a=[bm.verts.new(pc+t*u+Z*z+n*o0) for u,z in pts]; b=[bm.verts.new(pc+t*u+Z*z+n*o1) for u,z in pts]
        bm.faces.new(list(reversed(a))).material_index=mi; bm.faces.new(b).material_index=mi
        for k in range(len(pts)): bm.faces.new([a[k],a[(k+1)%len(a)],b[(k+1)%len(b)],b[k]]).material_index=mi
    def flat(bm,pc,t,n,pts,o,mi):
        bm.faces.new([bm.verts.new(pc+t*u+Z*z+n*o) for u,z in pts]).material_index=mi
    # window part material idx: 0 red,1 spandrel,2 glass,3 dark,4 sill,5 bracket,6 stone,7 stucco
    def member(pc,t,n,u0,z0,u1,z1,fw,mi=0,o0=0.07,o1=0.15):
        # straight frame member from (u0,z0) to (u1,z1)
        A=pc+t*u0+Z*z0; B=pc+t*u1+Z*z1; d=B-A; L=d.length
        if L<1e-3: return
        ax=d/L; ay=n; az=ax.cross(ay).normalized()
        box(bmW,(A+B)/2+n*((o0+o1)/2),ax,ay,az,L/2+fw/2,(o1-o0)/2,fw/2,mi)
    def window(pc,t,n,w,zb,zt,arch,spand=(),lights=3,transom=True):
        pts=outline(w,zb,zt,arch)
        prism(bmC,pc,t,n,pts,-0.15,P+0.15,0)
        flat(bmW,pc,t,n,pts,0.035,3); flat(bmW,pc,t,n,pts,0.085,2)
        fw=0.07
        for k in range(len(pts)): 
            (u0,z0),(u1,z1)=pts[k],pts[(k+1)%len(pts)]
            member(pc,t,n,u0,z0,u1,z1,fw)
        top=zt-w/2 if arch else zt
        for k in range(1,lights): u=-w/2+w*k/lights; member(pc,t,n,u,zb,u,(zt-(w/2-math.sqrt(max(0,(w/2)**2-u*u)))) if arch else zt,0.05)
        if arch: member(pc,t,n,-w/2,top,w/2,top,0.06)
        # storey transoms + spandrels
        hs=zt-zb
        for (s0,s1) in spand:
            box(bmW,pc+Z*((s0+s1)/2)+n*0.11,t,n,Z,w/2,0.035,(s1-s0)/2,1)
        if transom and not spand and hs<3.2 and not arch: member(pc,t,n,-w/2,zb+hs*0.72,w/2,zb+hs*0.72,0.05)
        box(bmW,pc+Z*(zb-0.04)+n*(P/2+0.05),t,n,Z,w/2+0.12,P/2+0.08,0.045,4)   # sill in the reveal, projecting
    # corner convexity
    def tv(i): return (poly[(i+1)%NP]-poly[i]).normalized()
    def convex(i):  # corner at poly[i] between edge i-1 and i
        a=tv(i-1); b=tv(i); c=a.x*b.y-a.y*b.x
        return (c>0)==(area>0)
    PHOTO={0:['tallarch','arch3','tallcenter','arch3','arch3'],2:['plain'],4:['arch3'],8:['arch3','tall']}
    DP=[tuple(p) for p in bpy.context.scene.get('qe_door_pts',[])]
    info=[]; nwin=0; nbr=0; belts=[]
    for i in range(NP):
        a,b=poly[i],poly[(i+1)%NP]; e=b-a; L=e.length; t2=e.normalized()
        n2=Vector((t2.y,-t2.x)) if area>0 else Vector((-t2.y,t2.x)); t=Vector((t2.x,t2.y,0)); n=Vector((n2.x,n2.y,0))
        ua=0.0; ub=L
        if convex((i+1)%NP): ub=L+P
        if not convex(i): ua=P
        # runs by local wall top
        us=[min(L-0.05,max(0.05,k*0.5)) for k in range(int(L/0.5)+1)]
        prof=[(u,wall_at(a+t2*u)) for u in us]; prof=[(u,w) for u,w in prof if w]
        if not prof: continue
        runs=[]; 
        for u,(zb,zt) in prof:
            if runs and abs(runs[-1][3]-zt)<0.4: runs[-1][1]=u; runs[-1][2]=min(runs[-1][2],zb)
            else: runs.append([u,u,zb,zt])
        for r_i,(r0,r1,zb,zt) in enumerate(runs):
            u0=ua if r_i==0 else r0; u1=ub if r_i==len(runs)-1 else (r1+runs[r_i+1][0])/2
            if r_i>0: u0=(runs[r_i-1][1]+r0)/2
            Lr=u1-u0
            if Lr<0.3: continue
            pc0=Vector((a.x,a.y,0))
            # slab
            ztS=zt-0.35
            box(bmS,pc0+t*((u0+u1)/2)+Z*((zb-0.05+ztS)/2)+n*(0.01+(P-0.01)/2),t,n,Z,Lr/2,(P-0.01)/2,(ztS-(zb-0.05))/2,0)
            box(bmW,pc0+t*((u0+u1)/2)+Z*(ztS-0.16)+n*(P+0.05),t,n,Z,Lr/2+0.05,0.06,0.13,7)   # top cornice band
            # plinth course (tan ashlar) + top cornice
            pm=a+t2*((u0+u1)/2)+n2*1.0; okg,lg,*_=bpy.context.scene.ray_cast(dg,Vector((pm.x,pm.y,zb+0.5)),Vector((0,0,-1)))
            gnd=lg.z if okg else zb
            if gnd>zb-0.8: box(bmW,pc0+t*((u0+u1)/2)+Z*(zb+0.45)+n*(P+0.03),t,n,Z,Lr/2+0.03,0.035,0.5,6)   # tan ashlar plinth only where the ground meets the wall base
            box(bmW,pc0+t*((u0+u1)/2)+Z*(zb+0.97)+n*(P+0.05),t,n,Z,Lr/2+0.05,0.06,0.05,7)
            hh=zt-zb; ns=4 if hh>14 else 3 if hh>10.5 else 2 if hh>7 else 1 if hh>3.0 else 0
            info.append((i,round(u0,1),round(u1,1),round(zb,2),round(zt,2),ns))
            if ns==0 or Lr<3.0: 
                belts.append((pc0,t,n,u0,u1,zb,zt,[])); continue
            ST=(zt-zb-1.0)/ns
            k=max(1,round((Lr-1.2)/4.7)); pitch=Lr/k
            types=PHOTO.get(i,None)
            occ=[]
            for j in range(k):
                uc=u0+pitch*(j+0.5); pc=pc0+t*uc
                if types: ty=types[j] if j<len(types) else 'arch3'
                else: ty='arch3' if (ns==4 and k>=3 and j%2==1) else 'plain'
                if any((Vector((x,y))-(a+t2*uc)).length<2.6 and zz>zb-1 for x,y,zz in DP): ty='plain'
                base=lambda s: zb+1.0+s*ST
                if ty.startswith('tall'):
                    w=min(pitch-1.1,3.6) if ty=='tallcenter' else min(pitch-1.3,2.8)
                    s_lo=0 if ty=='tall' else 1
                    if ty=='tallcenter':
                        # rect windows below, 2-storey arch over storeys 2-3 (photo centre bay)
                        window(pc,t,n,w,base(1)+0.55,base(2)-0.35,False,lights=3); nwin+=1
                        if ns>=4:
                            window(pc,t,n,w,base(2)+0.45,base(4)-0.25,True,spand=[(base(3)-0.05,base(3)+0.45)],lights=3); nwin+=1
                        window(pc,t,n,w,base(0)+0.35,base(1)-0.35,False,lights=3); nwin+=1
                        occ.append((uc-w/2,uc+w/2,base(1)-0.35,base(2)-0.35))
                    else:
                        sp=[(base(s)-0.25,base(s)+0.45) for s in range(s_lo+1,ns)]
                        window(pc,t,n,w,base(s_lo)+0.45,base(ns)-0.30,ty=='tallarch',spand=sp,lights=3); nwin+=1
                        if s_lo==1: window(pc,t,n,w,base(0)+0.35,base(1)-0.35,False,lights=3); nwin+=1
                        occ.append((uc-w/2,uc+w/2,base(s_lo),base(ns)))
                else:
                    w=min(pitch-1.5,2.7)
                    if w<0.9: continue
                    for s in range(ns):
                        ar=(ty=='arch3' and s==2 and ns>=4)
                        zb_=base(s)+(0.35 if s==0 else 0.55); zt_=base(s+1)-0.45+(0.25 if ar else 0)
                        if ar: zt_=min(zt_,base(s+1)-0.15)
                        window(pc,t,n,w,zb_,zt_,ar,lights=2 if w<1.8 else 3); nwin+=1
            belts.append((pc0,t,n,u0,u1,zb,zt,occ+[(0,0,0,0)],ST,ns))
            # deeper eave (photo: deep tile eaves on brackets): tilted tile/soffit slab continuing the LiDAR eave out to 1.4 m + dark-red fascia
            eave_ok=False
            if zt>150:
                qm=a+t2*((u0+u1)/2)+n2*0.5; r5=roof_at(qm)
                if r5 is not None and zt-1.0<r5<zt+1.0:
                    eave_ok=True; sl_=0.42; o0,o1=0.45,1.40; ea=u0-(0.9 if convex(i) or r_i>0 else 0); eb=u1+(0.0)
                    zt0=r5+0.05*sl_-0.015; zt1=zt0-(o1-0.5)*sl_
                    vs=[]
                    for (oo,zz) in ((o0,zt0),(o1,zt1)):
                        for uu in (ea,eb):
                            for dz in (0,-0.14): vs.append(bmW.verts.new(pc0+t*uu+n*oo+Z*(zz+dz)))
                    # vs index: o(0/1)*4 + u(0/1)*2 + dz(0/1)
                    F=[(0,2,6,4),(1,5,7,3),(4,6,7,5),(0,1,3,2),(0,4,5,1),(2,3,7,6)]
                    MI=[8,8,9,8,8,8]
                    for f,mi in zip(F,MI): bmW.faces.new([vs[k] for k in f]).material_index=mi
                    box(bmW,pc0+t*((ea+eb)/2)+n*(o1+0.02)+Z*(zt1-0.10),t,n,Z,(eb-ea)/2,0.025,0.13,5)
            # eave brackets at piers
            for j in range(k+1):
                ub_=u0+pitch*j
                if j==0: ub_+=0.35
                if j==k: ub_-=0.35
                q=a+t2*min(L-0.2,max(0.2,ub_))+n2*0.62; rz=roof_at(q)
                if rz is None or not (zt-1.0<rz<zt+1.0): continue
                ztop=rz-0.12; pc=pc0+t*ub_
                if eave_ok: ztop=rz-0.20; box(bmW,pc+Z*(ztop-0.14)+n*(0.01+0.55),t,n,Z,0.10,0.55,0.14,5)
                else: box(bmW,pc+Z*(ztop-0.14)+n*(0.01+0.31),t,n,Z,0.10,0.31,0.14,5)
                box(bmW,pc+Z*(ztop-0.48)+n*(P+0.11),t,n,Z,0.10,0.11,0.22,5)
                nbr+=1
    # belt course above storey 1 (skips tall openings)
    for bl in belts:
        if len(bl)<10: continue
        pc0,t,n,u0,u1,zb,zt,occ,ST,ns=bl; zbelt=zb+1.0+ST-0.1
        cuts=sorted([(o0,o1) for o0,o1,z0,z1 in occ if z0<zbelt+0.1<z1 and o1>o0])
        cur=u0
        for o0,o1 in cuts+[(u1,u1)]:
            if o0-0.05-cur>0.2: box(bmW,pc0+t*((cur+o0-0.05)/2)+Z*zbelt+n*(P+0.04),t,n,Z,(o0-0.05-cur)/2,0.04,0.07,7)
            cur=max(cur,o1+0.05)
    # entrances (photo montclarion: red double doors + transom, side door/sidelight, cornice canopy w/ lettering, red brackets, ashlar)
    lettered=False
    for (x,y,wz) in DP:
        p=Vector((x,y)); best=None
        for i in range(NP):
            a,b=poly[i],poly[(i+1)%NP]; e=b-a; L=e.length; t2=e/L; u=max(0,min(L,(p-a).dot(t2)))
            dd=(a+t2*u-p).length
            if best is None or dd<best[0]: best=(dd,i,u)
        _,i,u=best; a,b=poly[i],poly[(i+1)%NP]; t2=(b-a).normalized(); n2=Vector((t2.y,-t2.x)) if area>0 else Vector((-t2.y,t2.x))
        t=Vector((t2.x,t2.y,0)); n=Vector((n2.x,n2.y,0)); pc=Vector((a.x,a.y,0))+t*u; z0=wz+0.03
        def openings(du,w,h,lights,tr):
            pts=[(du-w/2,z0),(du+w/2,z0),(du+w/2,z0+h),(du-w/2,z0+h)]
            flat(bmW,pc,t,n,pts,0.10,3); flat(bmW,pc,t,n,pts,0.16,2)
            for k in range(4): (ua_,za),(ub2,zb2)=pts[k],pts[(k+1)%4]; member(pc,t,n,ua_,za,ub2,zb2,0.09,0,0.12,0.24)
            for k in range(1,lights): uu=du-w/2+w*k/lights; member(pc,t,n,uu,z0,uu,z0+(tr if tr else h),0.07,0,0.12,0.22)
            if tr: member(pc,t,n,du-w/2,z0+tr,du+w/2,z0+tr,0.08,0,0.12,0.22)
            box(bmW,pc+t*du+Z*(z0+1.05)+n*0.25,t,n,Z,0.012,0.012,0.35,0)   # pull handles
            if tr: member(pc,t,n,du-w/2,z0+0.12,du+w/2,z0+0.12,0.22,0,0.12,0.22)   # door bottom rail
        # recess block: stucco surround 0.30 proud with ashlar base
        for s_ in (-1,1): box(bmW,pc+t*(s_*3.55)+Z*(z0+0.38)+n*0.15,t,n,Z,0.65,0.12,0.41,6)   # ashlar base flanking the doors only
        openings(0,2.0,3.0,2,2.35); openings(-2.25,0.95,3.0,1,2.35); openings(2.25,0.95,3.0,1,None)
        # cornice canopy + fascia + brackets
        cz=z0+3.35
        box(bmW,pc+Z*(cz+0.35)+n*0.75,t,n,Z,3.6,0.70,0.35,7)
        box(bmW,pc+Z*(cz+0.74)+n*0.82,t,n,Z,3.75,0.78,0.06,7)
        for s_ in (-1,1): 
            box(bmW,pc+t*(s_*3.15)+Z*(cz-0.25)+n*0.30,t,n,Z,0.11,0.26,0.25,5); box(bmW,pc+t*(s_*3.15)+Z*(cz-0.6)+n*0.18,t,n,Z,0.11,0.14,0.15,5)
        box(bmW,pc+Z*(z0-0.06)+n*1.2,t,n,Z,3.8,1.2,0.06,4)   # landing
        if not lettered:
            cu=bpy.data.curves.new('QF_CCIS_lettering','FONT'); cu.body='COMPUTING AND INFORMATION SCIENCE'; cu.align_x='CENTER'; cu.align_y='CENTER'
            cu.size=0.30; cu.extrude=0.008; cu.materials.append(let)
            to=bpy.data.objects.new('QF_CCIS_entrance_lettering_photo_location_UNVERIFIED',cu); to['qf']=1; col.objects.link(to)
            M=__import__('mathutils').Matrix
            rot=M(((t.x,Z.x,n.x),(t.y,Z.y,n.y),(t.z,Z.z,n.z))).to_4x4()
            to.matrix_world=M.Translation(pc+Z*(cz+0.33)+n*1.462)@rot
            sc=min(1.0,6.4/ (0.30*0.62*len(cu.body))) ; to.scale=(sc,1,1); lettered=True
        info.append(('door',i,round(u,1),round(z0,2)))
    # skin = slab - cutters (exact)
    meS=bpy.data.meshes.new('QF_CCIS_skin_tmp'); bmS.to_mesh(meS); bmS.free(); meS.materials.append(stucco)
    meC=bpy.data.meshes.new('QF_CCIS_cut_tmp'); bmC.to_mesh(meC); bmC.free()
    oS=bpy.data.objects.new('QF_CCIS_skin_tmp',meS); oC=bpy.data.objects.new('QF_CCIS_cut_tmp',meC)
    bpy.context.scene.collection.objects.link(oS); bpy.context.scene.collection.objects.link(oC)
    md=oS.modifiers.new('cut','BOOLEAN'); md.operation='DIFFERENCE'; md.object=oC; md.solver='EXACT'
    dg=bpy.context.evaluated_depsgraph_get(); oE=oS.evaluated_get(dg)
    meF=bpy.data.meshes.new_from_object(oE); meF.name='QF_CCIS_stucco_skin_recessed_openings_photo'
    bpy.data.objects.remove(oS); bpy.data.objects.remove(oC); bpy.data.meshes.remove(meS); bpy.data.meshes.remove(meC)
    meF.materials.clear(); meF.materials.append(stucco)
    for pg in meF.polygons: pg.material_index=0
    sk=bpy.data.objects.new('QF_CCIS_stucco_skin_recessed_openings_photo',meF); sk['qf']=1; col.objects.link(sk)
    meW=bpy.data.meshes.new('QF_CCIS_windows_red_frames_spandrels_brackets_photo'); bmW.to_mesh(meW); bmW.free()
    for m in (red,spd,glassM,darkM,sillM,brk,stone,stucco,bpy.data.materials['Roof_tile_or_membrane'],bpy.data.materials['Eave_tile_top_soffit_under']): meW.materials.append(m)
    ow=bpy.data.objects.new('QF_CCIS_windows_red_frames_spandrels_brackets_photo',meW); ow['qf']=1; col.objects.link(ow)
    # qe: hide window/entrance object; keep its cover-wall windows as a recoloured copy
    q=bpy.data.objects[QEO]; q.hide_render=True; q.hide_viewport=True; q['qf_hidden']=1
    bm=bmesh.new(); bm.from_mesh(q.data); bm.transform(q.matrix_world)
    isl=[]; seen=set()
    for f in bm.faces:
        if f.index in seen: continue
        st=[f]; grp=[]; seen.add(f.index)
        while st:
            g=st.pop(); grp.append(g)
            for ed in g.edges:
                for h in ed.link_faces:
                    if h.index not in seen: seen.add(h.index); st.append(h)
        isl.append(grp)
    # windows on the OSM perimeter (within 0.7 m) -> drop; others (drape cover walls) keep
    def dperim(p):
        best=1e9
        for i in range(NP):
            a,b=poly[i],poly[(i+1)%NP]; e=b-a; L=e.length; u=max(0,min(L,(p-a).dot(e)/L)); best=min(best,(a+e*(u/L)-p).length)
        return best
    drop=[]; kept=0
    # group islands into window clusters by proximity of centroid to perimeter
    for grp in isl:
        c=sum((v.co for f in grp for v in f.verts),Vector())/sum(len(f.verts) for f in grp)
        if dperim(Vector((c.x,c.y)))<1.6: drop.extend(grp)
        else: kept+=1
    bmesh.ops.delete(bm,geom=list(set(drop)),context='FACES')
    meK=bpy.data.meshes.new('QF_qe_cover_wall_windows_red'); bm.to_mesh(meK); bm.free()
    for k_,m in enumerate(q.data.materials): meK.materials.append(m)
    meK.materials[0]=stucco; meK.materials[1]=red
    ok_=bpy.data.objects.new('QF_qe_cover_wall_windows_kept_red_UNVERIFIED',meK); ok_['qf']=1; col.objects.link(ok_)
    # OR lower-storey skirt windows on CCIS: object-level red frame override (shared brown material untouched)
    for o in bpy.data.objects:
        if o.name.startswith('OR_skirt_win_Center for Computing'):
            for si,sl in enumerate(o.material_slots):
                if sl.material and sl.material.name=='Window_frame_brown': sl.link='OBJECT'; sl.material=red; o['qf_slot']=si; print('QF_OR_red',o.name,si)
    # close-up camera on the west (photo) face
    a,b=poly[0],poly[1]; t2=(b-a).normalized(); n2=Vector((t2.y,-t2.x)) if area>0 else Vector((-t2.y,t2.x))
    p=a+t2*9.0; cpos=p+n2*13+t2*(-5); g=wall_at(p)[0]
    cd=bpy.data.cameras.new('QF_CAM_closeup_ccis_west_arches'); cd.lens=30; cd.clip_end=3000
    c=bpy.data.objects.new('QF_CAM_closeup_ccis_west_arches',cd); c['qf']=1; col.objects.link(c)
    c.location=(cpos.x,cpos.y,g+3.5); c.rotation_euler=(Vector((p.x,p.y,g+9.5))-c.location).to_track_quat('-Z','Y').to_euler()
    dg=bpy.context.evaluated_depsgraph_get(); p=a+t2*11.0; cp2=p+n2*30+t2*6; okg,lg,*_=bpy.context.scene.ray_cast(dg,Vector((cp2.x,cp2.y,200)),Vector((0,0,-1))); g2=lg.z if okg else 131
    cd=bpy.data.cameras.new('QF_CAM_eye_ccis_west_photo'); cd.lens=24; cd.clip_end=3000
    c=bpy.data.objects.new('QF_CAM_eye_ccis_west_photo',cd); c['qf']=1; col.objects.link(c)
    c.location=(cp2.x,cp2.y,g2+1.7); c.rotation_euler=(Vector((p.x,p.y,g2+11))-c.location).to_track_quat('-Z','Y').to_euler()
    print('QF_cam2',tuple(round(x,1) for x in c.location),okg and lg)
    print('QF_CCIS windows',nwin,'brackets',nbr,'skin polys',len(meF.polygons),'win polys',len(meW.polygons),'qe islands kept',kept,'of',len(isl))
    for x in info: print('QF_INFO',x)

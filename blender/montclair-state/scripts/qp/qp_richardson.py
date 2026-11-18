# qp: Richardson Hall (OSM 313027426) built in MAIN from the OSM footprint + 2017 B17 LiDAR levels + 1971-75 MSU archive slides
# (refs/web/20261102qo): brown-brick 1970s block 136.6->151.75 (recessed dark-glass ground storey under a soffit, middle-storey
# ribbon windows with a projecting sill band, top-storey punched windows, white fascia), four white windowless corner towers to
# 157.2 at the OSM jogs, middle penthouse + 4 roof units. ALL UNVERIFIED (current cladding, window counts, ground-floor recess).
# REVERT=1 removes everything recorded in data/qp/rich_added.json and restores moved trees.
import bpy, bmesh, json, os, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; J='data/qp/rich_added.json'; COL='QP_Richardson_Hall_UNVERIFIED'
if os.path.exists(J) and (REV or bpy.data.collections.get(COL)):
    d=json.load(open(J))
    for n in d['objects']:
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True)
    for k in ('meshes','materials','cameras'):
        for n in d[k]:
            x=getattr(bpy.data,k).get(n)
            if x and x.users==0: getattr(bpy.data,k).remove(x)
    c=bpy.data.collections.get(COL)
    if c: bpy.data.collections.remove(c)
    for n,loc in d['moved'].items():
        o=bpy.data.objects.get(n)
        if o: o.location=Vector(loc)
    print('QP_RICH reverted')
if not REV:
    before={k:set(x.name for x in getattr(bpy.data,k)) for k in ('objects','meshes','materials','cameras')}
    P=json.load(open('data/qp/rich_poly.json')); OUT=[Vector((x,y,0)) for x,y in P['outer']]; INS=[Vector((x,y,0)) for x,y in P['inset']]
    dsm={ (round(e['from'][0],2),round(e['from'][1],2)): e['dsm_2m_in_med_max'][0] for e in P['edges']}
    col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
    def mat(name,fn):
        m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']; fn(nt,b); return m
    def brick(nt,b):
        N=nt.nodes; L=nt.links.new; uv=N.new('ShaderNodeTexCoord'); bt=N.new('ShaderNodeTexBrick')
        bt.inputs['Color1'].default_value=(0.115,0.062,0.036,1); bt.inputs['Color2'].default_value=(0.15,0.085,0.05,1); bt.inputs['Mortar'].default_value=(0.26,0.24,0.21,1)
        bt.inputs['Scale'].default_value=1.0; bt.inputs['Mortar Size'].default_value=0.009; bt.inputs['Brick Width'].default_value=0.2; bt.inputs['Row Height'].default_value=0.067; bt.offset=0.5
        L(uv.outputs['UV'],bt.inputs['Vector'])
        nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.35; L(uv.outputs['UV'],nz.inputs['Vector'])
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=0.35
        L(bt.outputs['Color'],mx.inputs['A']); L(nz.outputs['Color'],mx.inputs['B']); L(mx.outputs['Result'],b.inputs['Base Color'])
        bm=N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value=0.25; bm.inputs['Distance'].default_value=0.004; L(bt.outputs['Fac'],bm.inputs['Height']); L(bm.outputs['Normal'],b.inputs['Normal'])
        b.inputs['Roughness'].default_value=0.85
    def white(nt,b):
        N=nt.nodes; L=nt.links.new; uv=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.8; nz.inputs['Detail'].default_value=6
        L(uv.outputs['UV'],nz.inputs['Vector']); cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.58,0.57,0.54,1); cr.color_ramp.elements[1].color=(0.74,0.73,0.70,1)
        L(nz.outputs['Fac'],cr.inputs['Fac']); L(cr.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.8
    def flat(c,r,met=0.0):
        def f(nt,b): b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=met
        return f
    M={'brick':mat('QP_Richardson_brick_brown_UNVERIFIED',brick),'white':mat('QP_Richardson_white_precast_UNVERIFIED',white),
       'glass':mat('QP_Richardson_glass_bronze_dark_UNVERIFIED',flat((0.035,0.032,0.028),0.06)),'mull':mat('QP_Richardson_mullion_bronze',flat((0.09,0.065,0.045),0.4,0.8)),
       'soffit':mat('QP_Richardson_soffit_concrete',flat((0.40,0.39,0.37),0.9)),'roof':mat('QP_Richardson_roof_membrane',flat((0.50,0.50,0.48),0.85)),
       'rtu':mat('QP_Richardson_roof_units_grey',flat((0.42,0.43,0.44),0.7)),'band':mat('QP_Richardson_precast_band_brown',flat((0.16,0.10,0.065),0.8))}
    def newobj(name,keys):
        me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me); col.objects.link(o)
        for k in keys: me.materials.append(M[k])
        o['UNVERIFIED_qp']='qp: Richardson Hall from OSM 313027426 + B17 LiDAR + 1971-75 archive slides'; return o,bmesh.new(),keys
    def face(bm,keys,pts,k,want=None):
        vs=[bm.verts.new(p) for p in pts]; f=bm.faces.new(vs); f.material_index=keys.index(k)
        f.normal_update()
        if want is not None and f.normal.dot(want)<0: f.normal_flip()
        return f
    def boxf(bm,keys,c,ax,ay,hx,hy,z0,z1,k):
        cs=[c+ax*sx*hx+ay*sy*hy for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        for i in range(4):
            a,b=cs[i],cs[(i+1)%4]; o=((a+b)/2-c); o.z=0
            face(bm,keys,[Vector((a.x,a.y,z0)),Vector((b.x,b.y,z0)),Vector((b.x,b.y,z1)),Vector((a.x,a.y,z1))],k,o)
        face(bm,keys,[Vector((p.x,p.y,z1)) for p in cs],k,Vector((0,0,1)))
    def finish(o,bm):
        uvl=bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            n=f.normal
            if abs(n.z)<0.5:
                t=Vector((-n.y,n.x,0)).normalized()
                for l in f.loops: l[uvl].uv=(l.vert.co.dot(t),l.vert.co.z)
            else:
                for l in f.loops: l[uvl].uv=(l.vert.co.x,l.vert.co.y)
        bm.to_mesh(o.data); bm.free()
    Z0,ZG,ZM,ZT,ZF,ZFT,ZR=136.6,142.3,146.9,151.0,151.0,151.75,151.55
    # --- upper block walls (brick) with openings
    o,bm,K=newobj('QP_Richardson_upper_block_UNVERIFIED',['brick','glass','mull','band','soffit','roof','white'])
    NW=[0]
    for i in range(len(OUT)):
        p0,p1=OUT[i],OUT[(i+1)%len(OUT)]; e=p1-p0; Ln=e.length; t=e/Ln; n=Vector((t.y,-t.x,0))
        tower=(dsm.get((round(p0.x,2),round(p0.y,2))) or 0)>155 or (Ln<7 and (dsm.get((round(p0.x,2),round(p0.y,2))) or 0)>153)
        P3=lambda u,z,dd=0: Vector((p0.x+t.x*u-n.x*dd,p0.y+t.y*u-n.y*dd,z))
        def wall(u0,u1,z0,z1,k='brick',dd=0): face(bm,K,[P3(u0,z0,dd),P3(u1,z0,dd),P3(u1,z1,dd),P3(u0,z1,dd)],k,n)
        def opening(u0,u1,z0,z1,D,mull=0):
            face(bm,K,[P3(u0,z0,0),P3(u1,z0,0),P3(u1,z0,D),P3(u0,z0,D)],'brick',Vector((0,0,1)))
            face(bm,K,[P3(u0,z1,0),P3(u1,z1,0),P3(u1,z1,D),P3(u0,z1,D)],'brick',Vector((0,0,-1)))
            face(bm,K,[P3(u0,z0,0),P3(u0,z1,0),P3(u0,z1,D),P3(u0,z0,D)],'brick',t)
            face(bm,K,[P3(u1,z0,0),P3(u1,z1,0),P3(u1,z1,D),P3(u1,z0,D)],'brick',-t)
            wall(u0,u1,z0,z1,'glass',D); NW[0]+=1
            if mull:
                m=max(1,round((u1-u0)/mull)); w=(u1-u0)/m
                for j in range(1,m):
                    uc=u0+j*w
                    for a,b,nn in ((uc-0.03,uc+0.03,n),):
                        face(bm,K,[P3(a,z0,D-0.07),P3(b,z0,D-0.07),P3(b,z1,D-0.07),P3(a,z1,D-0.07)],'mull',n)
                        face(bm,K,[P3(a,z0,D-0.07),P3(a,z1,D-0.07),P3(a,z1,D),P3(a,z0,D)],'mull',-t)
                        face(bm,K,[P3(b,z0,D-0.07),P3(b,z1,D-0.07),P3(b,z1,D),P3(b,z0,D)],'mull',t)
        if tower or Ln<4.0:
            wall(0,Ln,ZG,ZT); 
        else:
            m=0.7
            # middle storey: ribbon band
            wall(0,Ln,ZG,143.2); wall(0,m,143.2,145.7); wall(Ln-m,Ln,143.2,145.7); opening(m,Ln-m,143.2,145.7,0.16,1.5); wall(0,Ln,145.7,ZM)
            # projecting precast sill band
            for (a,b,c,d_,nn) in (((0,143.0,0.13),(Ln,143.0,0.13),(Ln,143.22,0.13),(0,143.22,0.13),n),):
                pass
            face(bm,K,[P3(0,143.0,-0.13),P3(Ln,143.0,-0.13),P3(Ln,143.22,-0.13),P3(0,143.22,-0.13)],'band',n)
            face(bm,K,[P3(0,143.22,-0.13),P3(Ln,143.22,-0.13),P3(Ln,143.22,0),P3(0,143.22,0)],'band',Vector((0,0,1)))
            face(bm,K,[P3(0,143.0,-0.13),P3(Ln,143.0,-0.13),P3(Ln,143.0,0),P3(0,143.0,0)],'band',Vector((0,0,-1)))
            # top storey: punched windows 0.9 x 1.9, ~3.0 m pitch
            nw=max(1,int((Ln-2.0)//3.0)); pitch=(Ln-1.6)/nw; zs0,zs1=147.9,149.8
            wall(0,Ln,ZM,zs0); wall(0,Ln,zs1,ZT); u=0.8
            for j in range(nw):
                c=0.8+pitch*(j+0.5); a,b=c-0.45,c+0.45
                wall(u,a,zs0,zs1); opening(a,b,zs0,zs1,0.2); u=b
            wall(u,Ln,zs0,zs1)
        # white fascia band, 6 cm proud
        face(bm,K,[P3(0,ZF,-0.06),P3(Ln,ZF,-0.06),P3(Ln,ZFT,-0.06),P3(0,ZFT,-0.06)],'white',n)
        face(bm,K,[P3(0,ZF,-0.06),P3(Ln,ZF,-0.06),P3(Ln,ZF,0),P3(0,ZF,0)],'white',Vector((0,0,-1)))
        face(bm,K,[P3(0,ZFT,-0.06),P3(Ln,ZFT,-0.06),P3(Ln,ZFT,0.25),P3(0,ZFT,0.25)],'white',Vector((0,0,1)))
        face(bm,K,[P3(0,ZR,0.25),P3(Ln,ZR,0.25),P3(Ln,ZFT,0.25),P3(0,ZFT,0.25)],'white',-n)
    face(bm,K,[Vector((p.x,p.y,ZG)) for p in OUT],'soffit',Vector((0,0,-1)))
    face(bm,K,[Vector((p.x,p.y,ZR)) for p in OUT],'roof',Vector((0,0,1)))
    finish(o,bm)
    # --- recessed ground storey: dark glass storefront on the 1.2 m inset + bronze mullions; brick piers on the outer line
    o,bm,K=newobj('QP_Richardson_ground_storey_glass_piers_UNVERIFIED',['glass','mull','brick'])
    for i in range(len(INS)):
        p0,p1=INS[i],INS[(i+1)%len(INS)]; e=p1-p0; Ln=e.length; t=e/Ln; n=Vector((t.y,-t.x,0))
        face(bm,K,[Vector((p0.x,p0.y,Z0)),Vector((p1.x,p1.y,Z0)),Vector((p1.x,p1.y,ZG)),Vector((p0.x,p0.y,ZG))],'glass',n)
        for j in range(1,int(Ln//1.6)+1):
            c=p0+t*(Ln*j/(int(Ln//1.6)+1))+n*0.04
            boxf(bm,K,c,t,n,0.035,0.04,Z0,ZG,'mull')
        tr=p0+n*0.04; boxf(bm,K,Vector((tr.x,tr.y,0)),t,n,Ln/2*0+0.0001,0.0001,ZG-0.01,ZG,'mull') if False else None
        # transom bar
        cc=(p0+p1)/2+n*0.05; boxf(bm,K,cc,t,n,Ln/2,0.05,139.6,139.7,'mull')
    for i in range(len(OUT)):
        p0,p1=OUT[i],OUT[(i+1)%len(OUT)]; e=p1-p0; Ln=e.length
        if Ln<12: continue
        t=e/Ln; n=Vector((t.y,-t.x,0)); k=max(2,round(Ln/7.5))
        for j in range(1,k):
            c=p0+t*(Ln*j/k)-n*0.45; boxf(bm,K,c,t,n,0.3,0.3,Z0,ZG+0.001,'brick')
    finish(o,bm)
    # --- white corner towers (rectangles from the OSM jogs), 5 cm proud of the block line
    TW={'N':[(72.82,292.19),(75.18,297.61),(80.72,295.22)],'E':[(107.8,282.77),(115.44,279.78),(113.15,273.96)],
        'S':[(97.46,236.96),(94.87,231.03),(89.52,233.34)],'W':[(59.2,246.44),(53.51,248.9),(55.59,253.67)]}
    o,bm,K=newobj('QP_Richardson_white_corner_towers_UNVERIFIED',['white'])
    for nm,(a,b,c) in TW.items():
        a,b,c=Vector((*a,0)),Vector((*b,0)),Vector((*c,0)); d_=a+(c-b); ctr=(a+c)/2
        ax=(b-a); hx=ax.length/2+0.17; ax.normalize(); ay=(c-b); hy=ay.length/2+0.17; ay.normalize()
        boxf(bm,K,ctr,ax,ay,hx,hy,Z0,157.0,'white')
        boxf(bm,K,ctr,ax,ay,hx+0.08,hy+0.08,157.0,157.2,'white')   # coping cap
    finish(o,bm)
    # --- roof: middle penthouse (B17 156.47) + small units (B17 153.1-154.8); positions from the Oct 14 level table
    A=Vector((math.cos(math.radians(-23.7)),math.sin(math.radians(-23.7)),0)); B=Vector((math.cos(math.radians(66.3)),math.sin(math.radians(66.3)),0))
    o,bm,K=newobj('QP_Richardson_roof_penthouse_units_UNVERIFIED',['white','rtu'])
    boxf(bm,K,Vector((89,273.5,0)),A,B,3.6,5.2,ZR-0.05,156.47,'white')
    for (x,y,z) in ((89.5,259,153.4),(78.5,263.5,154.6),(71.5,268,153.1),(84,249.5,153.9)):
        boxf(bm,K,Vector((x,y,0)),A,B,1.3,1.6,ZR-0.05,z,'rtu')
    finish(o,bm)
    # --- terrain check + tree clearance
    dg=bpy.context.evaluated_depsgraph_get(); T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; Te=T.evaluated_get(dg); Mi=T.matrix_world.inverted()
    def gz(x,y):
        ok,loc,nr,ix=Te.ray_cast(Mi@Vector((x,y,400)),Mi.to_3x3()@Vector((0,0,-1)),depsgraph=dg)
        return (T.matrix_world@loc).z if ok else None
    gs=[gz(p.x,p.y) for p in OUT]+[gz(84,264),gz(70,270),gz(100,260)]
    print('QP_GROUND',[None if g is None else round(g,2) for g in gs])
    from mathutils.geometry import intersect_point_line
    def dist_out(p):
        best=1e9
        for i in range(len(OUT)):
            a,b=OUT[i],OUT[(i+1)%len(OUT)]; q,f=intersect_point_line(p,a,b); f=min(max(f,0),1); q=a+(b-a)*f; best=min(best,(p-q).length)
        return best
    def inside(p):
        c=False; j=len(OUT)-1
        for i in range(len(OUT)):
            a,b=OUT[i],OUT[j]
            if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x: c=not c
            j=i
        return c
    moved={}; ctrB=Vector((84,264,0))
    for ob in bpy.data.objects:
        if not ob.name.startswith('T_') or ob.hide_render: continue
        p=Vector((ob.location.x,ob.location.y,0))
        if abs(p.x-84)>60 or abs(p.y-264)>60: continue
        dd=dist_out(p); ins=inside(p)
        if ins or dd<3.5:
            moved[ob.name]=list(ob.location); dirv=(p-ctrB).normalized(); step=0
            while (inside(p) or dist_out(p)<3.5) and step<80: p=p+dirv*0.25; step+=1
            g=gz(p.x,p.y); dz=(g-gz(ob.location.x,ob.location.y)) if g is not None and gz(ob.location.x,ob.location.y) is not None else 0
            ob.location=Vector((p.x,p.y,ob.location.z+dz))
    print('QP_TREES_MOVED',len(moved),{k:[round(v,1) for v in moved[k]] for k in moved})
    # --- cameras
    def cam(name,loc,tgt,lens,eye=None):
        cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=3000; co=bpy.data.objects.new(name,cd); col.objects.link(co)
        if eye is not None:
            g=gz(loc[0],loc[1]); loc=(loc[0],loc[1],(g if g else 137.8)+eye)
        L=Vector(loc); co.location=L; co.rotation_euler=(Vector(tgt)-L).to_track_quat('-Z','Y').to_euler(); return co
    cam('QP_CAM_oblique_richardson_from_S',(52,175,205),(85,262,146),28)
    cam('QP_CAM_eye_richardson_from_SE',(135,245,138.48),(103,263,146.0),26)
    cam('QP_CAM_eye_richardson_from_W',(30,262,138.85),(64,272,146.0),26)
    cam('QP_CAM_closeup_richardson_S_tower',(84,222,0),(86,239,145.5),30,1.65)
    print('QP_WINDOWS',NW[0])
    after={k:set(x.name for x in getattr(bpy.data,k)) for k in before}
    d={k:sorted(after[k]-before[k]) for k in before}; d['moved']=moved
    json.dump(d,open(J,'w'),indent=0); print('QP_RICH built',{k:len(v) for k,v in d.items()})

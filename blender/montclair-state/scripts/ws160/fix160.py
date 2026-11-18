# ws160: UNIFY #64 Panzer gym/S-block roof = LiDAR plane fits (prep/ws160_gymroof/fit160.json) + walls/partitions/fascia/coping/vent/units;
#        #63 residual: WS105 walkway remnant duplicate clipped, N walk ext re-graded to a straight 2 % ramp; gooseneck lanterns
import bpy, bmesh, math, json
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
def AB(v): w=Vector((v.x,v.y,0))-O; return w.dot(A), w.dot(B)
F=json.load(open(M+'prep/ws160_gymroof/fit160.json'))
NG,SG=F['N'],F['S']; ZM=F['mid']; ZX=F['annex']; ZB=117.0
col=bpy.data.collections.new('WS160_Panzer_gym_roof_planes_LiDAR'); bpy.context.scene.collection.children.link(col)
def mat(n,rgb,rough=0.6,metal=0.0):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal; return m
GYR=bpy.data.materials['WS158_gym_roof_grey_metal_UNVERIFIED']; GYW=bpy.data.materials['WS158_gym_wall_lightgrey_UNVERIFIED']
FAS=mat('WS160_gym_fascia_dark_bronze_UNVERIFIED',(0.10,0.09,0.08),0.5,0.4)
COP=mat('WS160_parapet_coping_aluminium_UNVERIFIED',(0.55,0.55,0.53),0.45,0.5)
MEM=mat('WS160_flat_roof_membrane_grey_UNVERIFIED',(0.36,0.36,0.35),0.85)
RTU=mat('WS160_rooftop_unit_lightgrey_UNVERIFIED',(0.62,0.63,0.62),0.5,0.3)
def obj(name,verts,faces,mats,mi=None,c=col):
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts],[],faces)
    for m in mats: me.materials.append(m)
    if mi:
        for p,k in zip(me.polygons,mi): p.material_index=k
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); c.objects.link(o); return o
def merge(parts):
    V=[];Fc=[];MI=[]
    for p in parts:
        v,f=p[0],p[1]; k=p[2] if len(p)>2 else 0
        o=len(V); V+=v; Fc+=[[i+o for i in q] for q in f]; MI+=[k]*len(f)
    return V,Fc,MI
def box(a0,a1,b0,b1,z0,z1,k=0):
    V=[P(a0,b0,z0),P(a1,b0,z0),P(a1,b1,z0),P(a0,b1,z0),P(a0,b0,z1),P(a1,b0,z1),P(a1,b1,z1),P(a0,b1,z1)]
    return V,[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]],k
def slabq(c4,th):  # 4 (a,b,z) top corners -> closed slab
    V=[P(a,b,z) for a,b,z in c4]+[P(a,b,z-th) for a,b,z in c4]
    return V,[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]
def zg(G,b): return G['zr']-G['s']*abs(b-G['br'])
# ---- retire old massing ----
for n in ('WS158_Panzer_gym_roof_LiDAR2023_massing_UNVERIFIED','WS158_Panzer_gym_walls_OSM_LiDAR_massing_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    if o: o.name=n[:40]+'_RETIRED_ws160'; o.hide_render=True; o.hide_viewport=True
# ---- gable roofs (two planes each, 0.18 m thick, overhang 0.35 eaves / 0.2 rakes) ----
def gable(G,a0,a1,b0,b1,ov=0.35,rk=0.2,nm=''):
    br=G['br']; e0=b0-ov; e1=b1+ov; A0=a0-rk; A1=a1+rk
    pl=[slabq([(A0,e0,zg(G,e0)),(A1,e0,zg(G,e0)),(A1,br,G['zr']),(A0,br,G['zr'])],0.18),
        slabq([(A0,br,G['zr']),(A1,br,G['zr']),(A1,e1,zg(G,e1)),(A0,e1,zg(G,e1))],0.18)]
    obj('WS160_Panzer_'+nm+'_gable_roof_LiDARfit_UNVERIFIED',*merge(pl)[:2],[GYR])
    # fascia (eaves + rakes), 0.28 deep, dark bronze
    fs=[box(A0,A1,e0-0.04,e0,zg(G,e0)-0.3,zg(G,e0)+0.02),box(A0,A1,e1,e1+0.04,zg(G,e1)-0.3,zg(G,e1)+0.02)]
    for aa,sgn in ((A0,-1),(A1,1)):
        for (u0,u1) in ((e0,br),(br,e1)):
            z0,z1=zg(G,u0),zg(G,u1); x0,x1=(aa-0.04,aa) if sgn<0 else (aa,aa+0.04)
            V=[P(x0,u0,z0-0.3),P(x1,u0,z0-0.3),P(x1,u1,z1-0.3),P(x0,u1,z1-0.3),P(x0,u0,z0+0.02),P(x1,u0,z0+0.02),P(x1,u1,z1+0.02),P(x0,u1,z1+0.02)]
            fs.append((V,[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]]))
    obj('WS160_Panzer_'+nm+'_fascia_rake_trim',*merge(fs)[:2],[FAS])
gable(NG,-14.3,33.55,-47.25,-9.0,nm='N_gym')
gable(SG,-67.9,-37.4,-40.7,-16.55,nm='S_gym')
sv=F['Svent']
obj('WS160_Panzer_S_gym_ridge_vent_LiDAR_UNVERIFIED',*merge([box(sv['a0'],sv['a1'],sv['b0'],sv['b1'],SG['zr']-0.3,sv['z'])])[:2],[FAS])
# ---- flat roofs ----
fl=[box(-37.4,-14.3,-45.3,-12.3,ZM-0.2,ZM),box(-1.0,13.1,-54.7,-47.25,ZX-0.2,ZX),box(13.1,21.6,-53.8,-47.25,ZX-0.2,ZX)]
obj('WS160_Panzer_flat_roofs_membrane_LiDAR',*merge(fl)[:2],[MEM])
# ---- walls: outline segments (a/b) with tops from the section roof functions ----
def zfun(a,b):
    if a>=-14.3:
        if b<-47.25: return ZX+0.25
        return zg(NG,b)
    if a>=-37.4: return ZM+0.28
    return zg(SG,b)
J=json.load(open(M+'prep/ws158_PanzerE/panzer158.json')); o=J['outer']
if o[0]==o[-1]: o=o[:-1]
gp=[AB(Vector((x,y,0))) for i,(x,y) in enumerate(o) if not (23<=i<=29)]
WV=[];WF=[];CP=[]
def wall(p0,p1,ztop=None,zbot=None):
    L=math.hypot(p1[0]-p0[0],p1[1]-p0[1]); n=max(1,int(math.ceil(L/0.5)))
    for k in range(n):
        t0,t1=k/n,(k+1)/n; q0=(p0[0]+(p1[0]-p0[0])*t0,p0[1]+(p1[1]-p0[1])*t0); q1=(p0[0]+(p1[0]-p0[0])*t1,p0[1]+(p1[1]-p0[1])*t1)
        m=((q0[0]+q1[0])/2,(q0[1]+q1[1])/2)
        # evaluate both ends with the section of the midpoint (nudged inward-agnostic)
        def zt(q):
            if ztop: return ztop(q)
            sa=m[0]; 
            if sa>=-14.3: return (ZX+0.25) if m[1]<-47.25 else zg(NG,q[1])
            if sa>=-37.4: return ZM+0.28
            return zg(SG,q[1])
        zb=(lambda q:ZB) if zbot is None else zbot
        b_=len(WV); WV.extend([P(q0[0],q0[1],zb(q0)),P(q1[0],q1[1],zb(q1)),P(q1[0],q1[1],zt(q1)),P(q0[0],q0[1],zt(q0))]); WF.append([b_,b_+1,b_+2,b_+3])
# snap near-boundary a values to section edges so gable ends land exactly
gp2=[]
for a,b in gp:
    for e in (-14.3,-37.4):
        if abs(a-e)<0.25: a=e
    gp2.append((a,b))
for i in range(len(gp2)):
    p0,p1=gp2[i],gp2[(i+1)%len(gp2)]
    wall(p0,p1)
    ma=(p0[0]+p1[0])/2
    if -37.4<=ma<-14.3 or (ma>=-14.3 and (p0[1]+p1[1])/2<-47.25):  # parapet coping on flat-roof sections
        zc=(ZM+0.28) if ma<-14.3 else (ZX+0.25)
        d=Vector((p1[0]-p0[0],p1[1]-p0[1],0))
        if d.length>0.05:
            d.normalize(); nn=Vector((-d.y,d.x,0))*0.18
            c=[(p0[0]-nn.x,p0[1]-nn.y),(p1[0]-nn.x,p1[1]-nn.y),(p1[0]+nn.x,p1[1]+nn.y),(p0[0]+nn.x,p0[1]+nn.y)]
            CP.append(slabq([(x,y,zc+0.06) for x,y in c],0.08))
# partitions: N gable end above mid roof, mid parapet above S roof, N eave wall above annex
wall((-14.3,-44.1),(-14.3,-12.3),ztop=lambda q:max(zg(NG,q[1]),ZM+0.28),zbot=lambda q:min(zg(NG,q[1]),ZM)-0.05)
wall((-37.4,-40.7),(-37.4,-16.55),ztop=lambda q:ZM+0.28,zbot=lambda q:zg(SG,q[1])-0.05)
wall((-1.0,-47.25),(21.6,-47.25),ztop=lambda q:zg(NG,-47.25),zbot=lambda q:ZX-0.05)
obj('WS160_Panzer_gym_walls_OSM_roofplanes_UNVERIFIED',WV,WF,[GYW])
obj('WS160_Panzer_parapet_coping',*merge(CP)[:2],[COP])
# ---- rooftop units (LiDAR blobs; seam/edge blobs dropped) ----
U=[]
for u in F['units']:
    if u['b1']>-13.5 or u['b1']-u['b0']>12: continue
    base=ZM if u['src']=='mid' else zg(NG,(u['b0']+u['b1'])/2)
    if u['src']=='N': base=zg(NG,u['b0'])
    U.append(box(u['a0'],u['a1'],u['b0'],u['b1'],base-0.2,u['z']))
U.append(box(-23.0,-21.0,-35.8,-14.6,ZM-0.1,133.0))  # mechanical row along a -22 (LiDAR 132.7-133.3)
obj('WS160_Panzer_rooftop_units_LiDAR_UNVERIFIED',*merge(U)[:2],[RTU])
print('FIX160 roof done units',len(U))
# ================= #63 residual =================
tot=0
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.name.startswith('WS105_PanzerE_lower_walkway'):
        me=ob.data; mw=ob.matrix_world
        cand=[p.index for p in me.polygons if (lambda q: 20.0<=q[0]<=34.0 and -3.0<=q[1]<=5.0)(AB(mw@p.center))]
        if cand:
            if me.users>1: ob.data=me.copy(); me=ob.data
            bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.faces[i] for i in cand],context='FACES'); bm.to_mesh(me); bm.free(); tot+=len(cand)
print('FIX160 WS105 remnant faces clipped',tot)
ext=bpy.data.objects.get('WS159b_PanzerE_front_walk_ext_N_LiDAR')
if ext:
    mw=ext.matrix_world; inv=mw.inverted()
    for v in ext.data.vertices:
        w=mw@v.co; a,b=AB(w); top=w.z>0  # classify by original top/bottom using offsets below
    # rebuild z: top = 122.31 + (a-25)*0.0357 (2 % ramp to LiDAR 122.56 at a 32), bottom = top-0.15
    zs=sorted(set(round((mw@v.co).z,3) for v in ext.data.vertices))
    for v in ext.data.vertices:
        w=mw@v.co; a,b=AB(w)
        # vertices come in top/bottom pairs per (a,b); the higher of the pair is the top
        pass
    import collections
    grp=collections.defaultdict(list)
    for v in ext.data.vertices:
        w=mw@v.co; a,b=AB(w); grp[(round(a,2),round(b,2))].append(v)
    for (a,b),vs in grp.items():
        vs.sort(key=lambda v:(mw@v.co).z)
        zt=122.31+max(0.0,a-25.0)*0.0357
        for v,zz in zip(vs,(zt-0.15,zt)):
            w=mw@v.co; w.z=zz; v.co=inv@w
    ext.data.update(); print('FIX160 ext regraded',len(grp))
# N-wing bed edge closed to the spur (a 24.0 -> 24.25)
mb=bpy.data.materials['WS159_mulch_dark_shredded']; ed=bpy.data.materials['WS159_bed_edge_concrete_curb']
c159=bpy.data.collections['WS159_Panzer_front_walk_beds']
obj('WS160_PanzerE_N_wing_bed_close_to_spur',*merge([box(24.0,24.3,-1.7,-0.12,122.07,122.27)])[:2],[mb],c=c159)
# ---- gooseneck lanterns replace the boxy WS159 lanterns (cch_1: black gooseneck arm, dome shade) ----
for n in ('WS159_PanzerE_wall_lanterns_black_UNVERIFIED','WS159_PanzerE_wall_lantern_glass'):
    o=bpy.data.objects.get(n)
    if o: bpy.data.objects.remove(o)
BLK=bpy.data.materials['WS159_lantern_black_metal']; LGL=bpy.data.materials['WS159_lantern_glass_frosted']
for i,a in enumerate((0.9,6.4,11.9,17.4)):
    cu=bpy.data.curves.new('WS160_gooseneck_arm_%d'%i,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=0.022; cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    pts=[(a,0.02,126.35),(a,0.30,126.62),(a,0.55,126.45)]
    for bp,(pa,pb,pz) in zip(sp.bezier_points,pts):
        bp.co=P(pa,pb,pz); bp.handle_left_type=bp.handle_right_type='AUTO'
    cu.materials.append(BLK); co=bpy.data.objects.new(cu.name,cu); c159.objects.link(co)
    # wall plate
    obj('WS160_gooseneck_plate_%d'%i,*merge([box(a-0.07,a+0.07,0.0,0.03,126.25,126.45)])[:2],[BLK],c=c159)
    # dome shade (cone frustum) + frosted lens
    bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=16,radius1=0.17,radius2=0.04,depth=0.13)
    me=bpy.data.meshes.new('WS160_gooseneck_shade_%d'%i); bm.to_mesh(me); bm.free(); me.materials.append(BLK)
    so=bpy.data.objects.new(me.name,me); so.location=P(a,0.55,126.38); c159.objects.link(so)
    bm=bmesh.new(); bmesh.ops.create_circle(bm,cap_ends=True,segments=16,radius=0.15)
    me=bpy.data.meshes.new('WS160_gooseneck_lens_%d'%i); bm.to_mesh(me); bm.free(); me.materials.append(LGL)
    lo=bpy.data.objects.new(me.name,me); lo.location=P(a,0.55,126.312); c159.objects.link(lo)
print('FIX160 lanterns')
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws160a.blend',compress=True)
print('FIX160 SAVED')

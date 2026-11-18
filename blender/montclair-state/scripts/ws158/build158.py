# ws158: Panzer Athletic Center E wing / 2009 lobby (layers: building on existing ground/road) + gym LiDAR massing
import bpy, bmesh, json, math, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
G0=122.25; ZB=117.0
col=bpy.data.collections.new('WS158_Panzer_Athletic_Center'); bpy.context.scene.collection.children.link(col)
def mat(n,rgb,rough=0.6,metal=0.0,emit=None):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    return m
STU=mat('WS158_stucco_white_smooth',(0.80,0.79,0.74),0.75)
RED=mat('WS158_red_standing_seam_metal',(0.36,0.06,0.04),0.45,0.35)
FAS=mat('WS158_fascia_redbrown',(0.30,0.07,0.05),0.5)
GLS=mat('WS158_glass_dark_reflective',(0.03,0.04,0.05),0.08,0.6)
FRW=mat('WS158_frame_white',(0.85,0.85,0.83),0.5)
FRR=mat('WS158_storefront_frame_darkred',(0.22,0.05,0.04),0.5)
LET=mat('WS158_letters_charcoal',(0.05,0.05,0.05),0.5)
GYW=mat('WS158_gym_wall_lightgrey_UNVERIFIED',(0.62,0.62,0.60),0.8)
GYR=mat('WS158_gym_roof_grey_metal_UNVERIFIED',(0.42,0.43,0.43),0.55,0.2)
def obj(name,polys,mats):
    me=bpy.data.meshes.new(name); verts=[]; fs=[]; mi=[]
    for (pts,k) in polys:
        base=len(verts); verts+= [tuple(p) for p in pts]; fs.append(list(range(base,base+len(pts)))); mi.append(k)
    me.from_pydata(verts,[],fs); 
    for m in mats: me.materials.append(m)
    for p,k in zip(me.polygons,mi): p.material_index=k
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
def boxw(a0,a1,b0,b1,z0,z1,k=0):
    c=[P(a0,b0,0),P(a1,b0,0),P(a1,b1,0),P(a0,b1,0)]; L=[]
    for i in range(4):
        p,q=c[i],c[(i+1)%4]; L.append(([p+Vector((0,0,z0)),q+Vector((0,0,z0)),q+Vector((0,0,z1)),p+Vector((0,0,z1))],k))
    L.append(([c[3]+Vector((0,0,z1)),c[2]+Vector((0,0,z1)),c[1]+Vector((0,0,z1)),c[0]+Vector((0,0,z1))],k))
    return L
def hip(a0,a1,b0,b1,ze,zr,ridge_b,ov,k=0,kf=1,ridge_along='a',back_flush=False):
    # eave rectangle with overhang; ridge line along 'a' at b=ridge_b inset so that all hips have the same slope
    s=(zr-ze)
    if ridge_along=='a':
        run=min(b1-ridge_b,ridge_b-b0); r0=a0+run; r1=a1-run
        if r1<r0: r0=r1=(a0+a1)/2
        dz=ov*s/run; E=[P(a0-ov,b0-ov,ze-dz),P(a1+ov,b0-ov,ze-dz),P(a1+ov,b1+ov,ze-dz),P(a0-ov,b1+ov,ze-dz)]
        R0=P(r0,ridge_b,zr); R1=P(r1,ridge_b,zr)
        F=[([E[0],E[1],R1,R0],k),([E[1],E[2],R1],k),([E[2],E[3],R0,R1],k),([E[3],E[0],R0],k)]
    else:  # ridge along b at a=(a0+a1)/2 running from back b0 to b1-run (front hip only, back flush to gym)
        ac=(a0+a1)/2; run=(a1-a0)/2; r1=b1-run*1.6; dz=ov*s/run
        E=[P(a0-ov,b0,ze-dz),P(a1+ov,b0,ze-dz),P(a1+ov,b1+ov,ze-dz),P(a0-ov,b1+ov,ze-dz)]
        R0=P(ac,b0,zr); R1=P(ac,r1,zr)
        F=[([E[1],E[2],R1,R0],k),([E[2],E[3],R1],k),([E[3],E[0],R0,R1],k),([E[0],E[1],R0],k)]
    # fascia band 0.25 m under the eave edge
    for i in range(4):
        p,q=E[i],E[(i+1)%4]; F.append(([p-Vector((0,0,0.28)),q-Vector((0,0,0.28)),q,p],kf))
        F.append(([p-Vector((0,0,0.28)),q-Vector((0,0,0.28)),q-Vector((0,0,0.28))+(E[(i+2)%4]-q).normalized()*0.0,p-Vector((0,0,0.28))],kf))
    return F
# --- pavilion (2009 lobby): a 0..18.3, b -11.5..0, eave 130.0, ridge 132.4 (LiDAR) ---
PA=(0.0,18.3,-11.5,0.0)
obj('WS158_PanzerE_lobby_pavilion_walls_stucco',boxw(*PA,ZB,130.0),[STU])
obj('WS158_PanzerE_lobby_pavilion_hip_roof_red_metal',hip(*PA,130.0,132.4,-5.75,0.6),[RED,FAS])
# wings (1 storey, eave 125.9, ridge 127.8 per LiDAR), front at b -1.8 / -1.7, back on the gym E wall b -9
obj('WS158_PanzerE_S_wing_walls_stucco',boxw(-4.9,0.0,-9.0,-1.8,ZB,125.9),[STU])
obj('WS158_PanzerE_S_wing_hip_roof_red_metal',hip(-4.9,0.0,-9.0,-1.8,125.9,127.8,0,0.5,ridge_along='b'),[RED,FAS])
obj('WS158_PanzerE_N_wing_walls_stucco',boxw(18.3,24.0,-9.0,-1.7,ZB,125.9),[STU])
obj('WS158_PanzerE_N_wing_hip_roof_red_metal',hip(18.3,24.0,-9.0,-1.7,125.9,127.8,0,0.5,ridge_along='b'),[RED,FAS])
# --- front details on the pavilion (b=0 face): 3 arched upper windows, 3 storefronts, lettering ---
F=[]
def rect(a0,a1,z0,z1,off,k): return ([P(a0,off,z0),P(a1,off,z0),P(a1,off,z1),P(a0,off,z1)],k)
def arch(ac,w,z0,zs,off,k,seg=14):
    r=w/2; pts=[P(ac-r,off,z0),P(ac+r,off,z0)]+[P(ac+r*math.cos(math.pi*i/seg),off,zs+r*math.sin(math.pi*i/seg)) for i in range(seg+1)]
    return (pts,k)
bay=18.3/3
for i in range(3):
    ac=bay*(i+0.5)
    F.append(arch(ac,2.9,126.0,128.15,0.02,1))      # white surround
    F.append(arch(ac,2.6,126.15,128.15,0.04,0))     # glass
    for t in (-0.43,0.43): F.append(rect(ac+t*1.3-0.03,ac+t*1.3+0.03,126.15,128.15+1.3*math.sqrt(1-t*t)-0.02,0.06,1))  # mullions
    for z in (127.0,127.9,128.15): F.append(rect(ac-1.3,ac+1.3,z-0.03,z+0.03,0.06,1))
    F.append(rect(ac-1.55,ac+1.55,122.3,125.0,0.02,2))  # storefront frame
    F.append(rect(ac-1.45,ac+1.45,122.4,124.9,0.04,0))
    F.append(rect(ac-0.02,ac+0.02,122.4,124.9,0.06,2)); F.append(rect(ac-1.45,ac+1.45,124.2,124.26,0.06,2))
    F.append(rect(ac-1.6,ac+1.6,125.0,125.12,0.05,1))  # sill/head band
o=obj('WS158_PanzerE_lobby_front_arched_windows_storefronts',F,[GLS,FRW,FRR])
# wing front windows (dark frame + grille), one per wing
W=[]
for (a0,a1,bf) in ((-4.9,0.0,-1.8),(18.3,24.0,-1.7)):
    ac=(a0+a1)/2
    W.append(([P(ac-1.1,bf+0.02,122.8),P(ac+1.1,bf+0.02,122.8),P(ac+1.1,bf+0.02,125.0),P(ac-1.1,bf+0.02,125.0)],1))
    W.append(([P(ac-1.0,bf+0.04,122.9),P(ac+1.0,bf+0.04,122.9),P(ac+1.0,bf+0.04,124.9),P(ac-1.0,bf+0.04,124.9)],0))
obj('WS158_PanzerE_wing_front_windows_UNVERIFIED',W,[GLS,FRR])
# lettering band PANZER / ATHLETIC / CENTER between the floors (cch_1)
for i,t in enumerate(('PANZER','ATHLETIC','CENTER')):
    cu=bpy.data.curves.new('WS158_letters_'+t,'FONT'); cu.body=t; cu.size=0.42; cu.align_x='CENTER'; cu.extrude=0.01
    lo=bpy.data.objects.new('WS158_PanzerE_lettering_'+t,cu); col.objects.link(lo); cu.materials.append(LET)
    lo.location=P(bay*(i+0.5),0.07,125.35); lo.rotation_euler=(math.pi/2,0,th-math.pi/2+math.pi)
    lo.rotation_euler=(math.pi/2,0,math.atan2(B.y,B.x)+math.pi/2)
# --- gym + S block massing from LiDAR ---
J=json.load(open(M+'scripts/ws158/gym158.json'))
GF=[([Vector(v) for v in f],0) for f in J['faces']]
obj('WS158_Panzer_gym_roof_LiDAR2023_massing_UNVERIFIED',GF,[GYR])
WL=[]
for x0,y0,z0,x1,y1,z1 in J['walls']:
    WL.append(([Vector((x0,y0,ZB)),Vector((x1,y1,ZB)),Vector((x1,y1,z1)),Vector((x0,y0,z0))],0))
obj('WS158_Panzer_gym_walls_OSM_LiDAR_massing_UNVERIFIED',WL,[GYW])
# info: what already sits inside the footprint
fp=[Vector(v[:2]+[0]) for v in []]
n=[ob.name for ob in bpy.data.objects if ob.type=='MESH' and -293<ob.location.x<-234 and -242<ob.location.y<-137 and not ob.name.startswith('WS158')]
print('BUILD158 objs w/ origin in Panzer bbox',len(n),n[:15])
print('BUILD158 new objs',len(col.objects))
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws158a.blend',copy=True)
print('SAVED_WS158A RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)

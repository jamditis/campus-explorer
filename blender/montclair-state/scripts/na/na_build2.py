# Session na pass 2: furnish the other 4 upper glass conference rooms + the 5 lower NJ PBS management offices
# (Joe Oct 29 10:45 PM: upstairs = glass conference rooms, downstairs = glass-walled NJ PBS management offices).
# Additive: new collection. Lay-in ceilings + troffers, carpet, white wall skins over the maroon partition boxes,
# conference tables + chairs + wall TV (upper), desk + monitor + credenza + guest chairs (lower). All UNVERIFIED.
import bpy, bmesh, math, os, random
from mathutils import Vector
MODE=os.environ.get('NA_MODE','TEST')
SES='na'; COLN='MS_CCOM_back_rooms_furnish_20261030na'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; UA=U0+0.35; UB=1.8; TM=-9.8; TBACK=-14.3; ZF=137.41; ZM1=141.85
edges=[UA+(UB-UA)*k/5 for k in range(6)]
IT0,IT1=TM-0.05,TBACK
SRC="Joe correction Oct 29 10:45 PM (upper glass conference rooms / lower NJ PBS management offices); furniture invented, UNVERIFIED"
mats=bpy.data.materials
M=lambda nm: mats[nm]
M_CARP=M('NA_ccm_striped_carpet_generic_UNVERIFIED'); M_CEIL=M('NA_ceiling_layin_tile_2ft_UNVERIFIED'); M_TROF=M('NA_troffer_2x2_emit_UNVERIFIED')
M_WALL=M('CCOM_int_wall_white_20261014v'); M_WOOD=M('NA_desk_top_warm_oak_laminate_UNVERIFIED'); M_STEEL=M('NA_desk_leg_black_steel_UNVERIFIED')
M_BEZ=M('MY_screen_bezel_black_UNVERIFIED'); M_SCR=M('MY_desk_monitor_screen_generic_UNVERIFIED'); M_TV=M('MY_tv_atlas_generic_broadcast_UNVERIFIED')
M_FILE=M('NA_file_pedestal_grey_metal_UNVERIFIED'); M_BASE=M('MY_rubber_cove_base_dark_grey_UNVERIFIED')
M_POT=M('NA_planter_dark_grey_UNVERIFIED'); M_LEAF=M('NA_plant_leaf_green_UNVERIFIED')
def mat(name,col,rough=0.6):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; m['msu_tag_session']=SES; return m
M_CPT2=mat('NA_office_carpet_tile_charcoal_UNVERIFIED',(0.10,0.10,0.11),0.95)
M_BOOK=[mat('NA_book_spine_%d_UNVERIFIED'%i,c,0.7) for i,c in enumerate(((0.35,0.06,0.05),(0.05,0.12,0.30),(0.75,0.72,0.65),(0.12,0.20,0.10)))]
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
col['msu_tag_session']=SES
def newobj(name,bm,mlist):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['msu_tag_session']=SES; o['status']='UNVERIFIED'; o['source']=SRC; return o
def box(bm,u0,u1,t0,t1,z0,z1,mi=0):
    vs=[bm.verts.new(P(u,t,z)) for z in (z0,z1) for t in (t0,t1) for u in (u0,u1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
def quad_uv(bm,pts,uvs,uvl,mi=0):
    f=bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index=mi
    for lp,uv in zip(f.loops,uvs): lp[uvl].uv=uv
B={k:bmesh.new() for k in ('carp','ceil','trof','skin','base','wood','steel','bez','scr','tv','file','book','pot','leaf')}
UVL={k:B[k].loops.layers.uv.verify() for k in ('carp','ceil','scr','tv')}
chairs=[]; T=0.6096
random.seed(42)
def cyl(bm,u,t,r0,r1,z0,z1,nseg=10):
    c=P(u,t,0)
    lo=[bm.verts.new(c+Vector((r0*math.cos(2*math.pi*k/nseg),r0*math.sin(2*math.pi*k/nseg),z0))) for k in range(nseg)]
    hi=[bm.verts.new(c+Vector((r1*math.cos(2*math.pi*k/nseg),r1*math.sin(2*math.pi*k/nseg),z1))) for k in range(nseg)]
    bm.faces.new(lo[::-1])
    for k in range(nseg): bm.faces.new([lo[k],lo[(k+1)%nseg],hi[(k+1)%nseg],hi[k]])
def plant(u,t,zf,h):
    cyl(B['pot'],u,t,0.12,0.15,zf,zf+0.32); c=P(u,t,zf+0.30)
    for k in range(12):
        a=random.uniform(0,2*math.pi); el=random.uniform(0.3,1.2); ln=random.uniform(0.4,h)
        dv=Vector((math.cos(a)*math.cos(el),math.sin(a)*math.cos(el),math.sin(el))); sd=Vector((-math.sin(a),math.cos(a),0))*random.uniform(0.05,0.09)
        tip=c+dv*ln; mid=c+dv*ln*0.5; B['leaf'].faces.new([B['leaf'].verts.new(x) for x in (c,mid+sd,tip,mid-sd)])
def shell(u0,u1,zf,zc,carpmat):
    IU0,IU1=u0+0.05,u1-0.05
    k='carp'
    quad_uv(B[k],[P(IU0,IT0,zf),P(IU1,IT0,zf),P(IU1,IT1,zf),P(IU0,IT1,zf)],[(IU0/2,IT0/2),(IU1/2,IT0/2),(IU1/2,IT1/2),(IU0/2,IT1/2)],UVL[k],mi=carpmat)
    quad_uv(B['ceil'],[P(IU0,IT1,zc),P(IU1,IT1,zc),P(IU1,IT0,zc),P(IU0,IT0,zc)],[(IU0/T,IT1/T),(IU1/T,IT1/T),(IU1/T,IT0/T),(IU0/T,IT0/T)],UVL['ceil'])
    um=(IU0+IU1)/2
    for (u,t) in ((um,-11.1),(um,-13.1)): box(B['trof'],u-0.29,u+0.29,t+0.29,t-0.29,zc-0.006,zc-0.001)
    box(B['skin'],IU0+0.001,IU0+0.011,IT0-0.01,IT1+0.002,zf,zc); box(B['skin'],IU1-0.011,IU1-0.001,IT0-0.01,IT1+0.002,zf,zc)
    box(B['skin'],IU0+0.011,IU1-0.011,IT1+0.012,IT1+0.002,zf,zc)
    box(B['base'],IU0+0.011,IU0+0.02,IT0-0.02,IT1+0.012,zf,zf+0.10); box(B['base'],IU1-0.02,IU1-0.011,IT0-0.02,IT1+0.012,zf,zf+0.10)
    box(B['base'],IU0+0.02,IU1-0.02,IT1+0.021,IT1+0.012,zf,zf+0.10)
    return IU0,IU1,um
def legs(u0,u1,t0,t1,zf,h):
    for uu in (u0+0.05,u1-0.08):
        for tt in (t0-0.05,t1+0.08): box(B['steel'],uu,uu+0.03,tt,tt-0.03,zf,zf+h-0.03)
def monitor(u,t,s,zf,w=0.55,h=0.33):
    zb=zf+0.74+0.12
    box(B['bez'],u-w/2,u+w/2,t,t-s*0.035,zb,zb+h); box(B['bez'],u-0.03,u+0.03,t-s*0.05,t-s*0.08,zf+0.74,zb+0.05); box(B['bez'],u-0.12,u+0.12,t,t-s*0.2,zf+0.74,zf+0.752)
    tt=t+s*0.002; p=[P(u-w/2+0.015,tt,zb+0.015),P(u+w/2-0.015,tt,zb+0.015),P(u+w/2-0.015,tt,zb+h-0.015),P(u-w/2+0.015,tt,zb+h-0.015)]
    ox=random.random()*0.5; uv=[(ox,0),(ox+0.5,0),(ox+0.5,1),(ox,1)]
    if s<0: p=[p[1],p[0],p[3],p[2]]; uv=[uv[1],uv[0],uv[3],uv[2]]
    quad_uv(B['scr'],p,uv,UVL['scr'])
# ---- upper conference rooms 0..3 (room 4 = CCM office, done in na pass 1) ----
for r in range(4):
    zf=ZM1+0.01; zc=144.86
    IU0,IU1,um=shell(edges[r],edges[r+1],zf,zc,0)
    # table along t, 1.0 x 2.6 m
    t0,t1=-10.85,-13.45
    box(B['wood'],um-0.5,um+0.5,t0,t1,zf+0.71,zf+0.74)
    for tt in (t0-0.35,t1+0.35): box(B['steel'],um-0.06,um+0.06,tt+0.06,tt-0.06,zf,zf+0.71); box(B['steel'],um-0.35,um+0.35,tt+0.05,tt-0.05,zf,zf+0.03)
    for tt in (-11.35,-12.15,-12.95):
        chairs.append((um-0.85,tt,(1,0),zf)); chairs.append((um+0.85,tt,(-1,0),zf))
    # wall TV on the back wall
    box(B['bez'],um-0.85,um+0.85,IT1+0.06,IT1+0.012,zf+1.05,zf+2.03)
    quad_uv(B['tv'],[P(um-0.82,IT1+0.062,zf+1.08),P(um+0.82,IT1+0.062,zf+1.08),P(um+0.82,IT1+0.062,zf+2.0),P(um-0.82,IT1+0.062,zf+2.0)],[(r*0.25,0),(r*0.25+0.25,0),(r*0.25+0.25,1),(r*0.25,1)],UVL['tv'])
    # credenza under TV
    box(B['file'],um-0.9,um+0.9,IT1+0.47,IT1+0.02,zf,zf+0.62)
    if r%2==0: plant(IU0+0.30,IT0-0.30,zf,0.7)
# ---- lower NJ PBS management offices 0..4 ----
for r in range(5):
    zf=ZF+0.005; zc=140.50
    IU0,IU1,um=shell(edges[r],edges[r+1],zf,zc,1)
    # desk facing the glass (user sits back side, faces +t toward the studio), L return
    du0,du1=um-0.85,um+0.85; dt0,dt1=-11.9,-12.65
    box(B['wood'],du0,du1,dt0,dt1,zf+0.71,zf+0.74); legs(du0,du1,dt0,dt1,zf,0.74)
    box(B['wood'],du1-0.6,du1,dt1,dt1-0.9,zf+0.71,zf+0.74); box(B['steel'],du1-0.08,du1-0.05,dt1-0.82,dt1-0.85,zf,zf+0.71)
    box(B['file'],du0+0.08,du0+0.48,dt0-0.10,dt1+0.10,zf+0.01,zf+0.62)
    monitor(um+0.05,dt1+0.18,1,zf)
    chairs.append((um,-13.15,(0,1),zf)); chairs.append((um-0.45,-10.9,(0,-1),zf)); chairs.append((um+0.45,-10.9,(0,-1),zf))
    # bookcase against the back wall
    bu0,bu1=IU0+0.25,IU0+1.15
    box(B['file'],bu0,bu1,IT1+0.05,IT1+0.02,zf,zf+1.80)                      # back panel
    for uu in (bu0,bu1-0.02): box(B['file'],uu,uu+0.02,IT1+0.38,IT1+0.05,zf,zf+1.80)   # sides
    for k in range(6):
        z=zf+0.02+k*0.356; box(B['file'],bu0+0.02,bu1-0.02,IT1+0.38,IT1+0.05,z-0.02 if k else zf,z+0.0 if k else zf+0.08)  # shelves + plinth
    box(B['file'],bu0,bu1,IT1+0.38,IT1+0.05,zf+1.78,zf+1.80)
    for k in range(4):
        z=zf+0.08+k*0.356 if k==0 else zf+0.02+k*0.356; uu=bu0+0.03; stop=bu0+0.03+random.uniform(0.45,0.82)
        while uu<stop:
            w=random.uniform(0.02,0.05); hgt=random.uniform(0.18,0.29)
            box(B['book'],uu,uu+w,IT1+0.33-random.uniform(0,0.03),IT1+0.08,z,z+hgt,mi=random.randrange(4)); uu+=w+0.002
    if r in (1,3): plant(IU1-0.35,IT0-0.35,zf,0.8)
mats_for={'carp':[M_CARP,M_CPT2],'ceil':[M_CEIL],'trof':[M_TROF],'skin':[M_WALL],'base':[M_BASE],'wood':[M_WOOD],'steel':[M_STEEL],'bez':[M_BEZ],'scr':[M_SCR],'tv':[M_TV],'file':[M_FILE],'book':M_BOOK,'pot':[M_POT],'leaf':[M_LEAF]}
names={'carp':'carpets','ceil':'lay-in ceilings','trof':'2x2 troffers (emissive)','skin':'white wall skins','base':'cove base','wood':'wood desk/table tops','steel':'black steel legs','bez':'monitor + TV bezels','scr':'monitor screens (generic)','tv':'wall TV screens (generic)','file':'credenzas/files/bookcases','book':'shelf books','pot':'planters','leaf':'plants (low-poly)'}
for k,bm in B.items(): newobj('CCOM back rooms %s (na)'%names[k],bm,mats_for[k])
chair=bpy.data.objects.get('MX proto task chair (hidden, instanced)'); ng=bpy.data.node_groups.get('MX_instance_proto_rot')
me=bpy.data.meshes.new('NA back-room chair points'); vs=[]; rots=[]
for u,t,(fu,ft),zf in chairs:
    vs.append(P(u,t,zf)); f=d*fu+n*ft; rots.append(math.atan2(f.y,f.x)+random.uniform(-0.3,0.3))
me.from_pydata(vs,[],[]); a=me.attributes.new('rot','FLOAT_VECTOR','POINT')
for i,r in enumerate(rots): a.data[i].vector=(0,0,r)
cp=bpy.data.objects.new('CCOM back rooms task chairs (na, GN instances of the mx proto)',me); col.objects.link(cp)
cp['msu_tag_session']=SES; cp['status']='UNVERIFIED'; cp['source']=SRC; cp['count']=len(chairs)
md=cp.modifiers.new('NA instances','NODES'); md.node_group=ng
sid=[it.identifier for it in ng.interface.items_tree if getattr(it,'in_out','')=='INPUT' and it.socket_type=='NodeSocketObject'][0]; md[sid]=chair
print("NEWOBJ",len(col.objects),"chairs",len(chairs))
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/na/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))

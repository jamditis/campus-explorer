# Session na (Oct 30 2026, ~3:25 AM ET): CCM office interior, far-left upper glass room above the NJ PBS studio
# (Joe Oct 29 10:45 PM + ref refs/joe_ccom_20261014/ccm_current_office_above_newsroom.jpg, Joe Oct 14).
# Additive: new collection; the mw placeholder 'carpet + desks' object is HIDDEN (scene['na_hidden']). All sizes UNVERIFIED.
import bpy, bmesh, math, os, random
from mathutils import Vector
MODE=os.environ.get('NA_MODE','TEST')
SES='na'; COLN='MS_CCM_office_interior_20261030na'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; UA=U0+0.35; UB=1.8; TM=-9.8; TBACK=-14.3; ZM1=141.85; ZTOP=144.9
edges=[UA+(UB-UA)*k/5 for k in range(6)]; E0,E1=edges[-2],edges[-1]
IU0,IU1=E0+0.05,E1-0.05            # partition faces
IT0,IT1=TM-0.05,TBACK              # glass-frame back face .. studio back wall face
ZFL=ZM1+0.01; ZCE=144.86
SRC="Joe photo refs/joe_ccom_20261014/ccm_current_office_above_newsroom.jpg (Oct 14) + Joe correction Oct 29 10:45 PM; layout/sizes UNVERIFIED"
mats=bpy.data.materials; HERE=os.path.dirname(bpy.data.filepath)
def mat(name,col,rough=0.6,metal=0.0,emit=None,es=0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=es
    m['msu_tag_session']=SES; return m
def imgmat(name,fn,rough=0.8,es=0.0):
    m=mats.get(name)
    if m: return m
    im=bpy.data.images.load(os.path.join(HERE,'textures/na',fn),check_existing=True); im.pack()
    m=mats.new(name); m.use_nodes=True; N=m.node_tree.nodes; b=N['Principled BSDF']
    tx=N.new('ShaderNodeTexImage'); tx.image=im
    m.node_tree.links.new(tx.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=rough
    if es: m.node_tree.links.new(tx.outputs['Color'],b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value=es
    m['msu_tag_session']=SES; m['status']='UNVERIFIED generic texture'; return m
M_CARP=imgmat('NA_ccm_striped_carpet_generic_UNVERIFIED','na_ccm_striped_carpet_generic_UNVERIFIED.jpg',0.95)
M_PAINT=imgmat('NA_ccm_abstract_painting_generic_UNVERIFIED','na_ccm_abstract_painting_generic_UNVERIFIED.png',0.7)
M_CEIL=imgmat('NA_ceiling_layin_tile_2ft_UNVERIFIED','na_ceiling_layin_tile_2ft_UNVERIFIED.png',0.9)
M_WOOD=mat('NA_desk_top_warm_oak_laminate_UNVERIFIED',(0.42,0.26,0.14),0.45)
M_STEEL=mat('NA_desk_leg_black_steel_UNVERIFIED',(0.015,0.015,0.016),0.4,metal=0.6)
M_PART=mat('NA_cubicle_fabric_grey_UNVERIFIED',(0.36,0.37,0.38),0.95)
M_PTRIM=mat('NA_cubicle_trim_aluminium_UNVERIFIED',(0.55,0.56,0.57),0.35,metal=0.8)
M_FILE=mat('NA_file_pedestal_grey_metal_UNVERIFIED',(0.48,0.49,0.50),0.4,metal=0.3)
M_WALL=mats.get('CCOM_int_wall_white_20261014v')
M_TROF=mat('NA_troffer_2x2_emit_UNVERIFIED',(0.95,0.95,0.95),0.4,emit=(1.0,0.98,0.94),es=9.0)
M_PRN=mat('NA_printer_white_plastic_UNVERIFIED',(0.78,0.78,0.76),0.5)
M_TOTE=mat('NA_storage_tote_sage_green_UNVERIFIED',(0.35,0.48,0.38),0.55)
M_BOX=mat('NA_cardboard_box_UNVERIFIED',(0.45,0.32,0.19),0.85)
M_BLUEB=mat('NA_recycling_bin_blue_UNVERIFIED',(0.02,0.12,0.45),0.5)
M_BLKB=mat('NA_trash_bin_black_UNVERIFIED',(0.02,0.02,0.02),0.5)
M_POT=mat('NA_planter_dark_grey_UNVERIFIED',(0.08,0.08,0.085),0.6)
M_LEAF=mat('NA_plant_leaf_green_UNVERIFIED',(0.05,0.20,0.04),0.6)
M_BEZ=mats.get('MY_screen_bezel_black_UNVERIFIED') or mat('NA_bezel',(0.01,0.01,0.012),0.5)
M_SCR=mats.get('MY_desk_monitor_screen_generic_UNVERIFIED') or mat('NA_screen',(0.1,0.2,0.4),0.3,emit=(0.2,0.3,0.5),es=0.7)
M_KB=mat('NA_keyboard_black_UNVERIFIED',(0.02,0.02,0.022),0.6)
M_FRAME=mat('NA_painting_canvas_edge_UNVERIFIED',(0.85,0.84,0.80),0.8)
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
col['msu_tag_session']=SES
def newobj(name,bm,mlist):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']='UNVERIFIED'; o['source']=SRC
    return o
def box(bm,u0,u1,t0,t1,z0,z1,mi=0):
    vs=[bm.verts.new(P(u,t,z)) for z in (z0,z1) for t in (t0,t1) for u in (u0,u1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
def fixnormals(bm): bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
def quad_uv(bm,pts,uvs,mi=0,uvl=None):
    f=bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index=mi
    uvl=uvl or bm.loops.layers.uv.verify()
    for lp,uv in zip(f.loops,uvs): lp[uvl].uv=uv
    return f
# ---- 0. hide the mw placeholder carpet + 3-desk slab ----
hidden=[]
o=bpy.data.objects.get('CCOM CCM office (upper far-left room) carpet + desks (mw)')
if o: o.hide_render=True; o.hide_viewport=True; hidden.append(o.name)
bpy.context.scene['na_hidden']=hidden
# ---- 1. carpet (UV in metres/2 -> one tile = 2 m), ceiling lay-in grid + troffers, white wall skins ----
bm=bmesh.new(); uvl=bm.loops.layers.uv.verify()
quad_uv(bm,[P(IU0,IT0,ZFL),P(IU1,IT0,ZFL),P(IU1,IT1,ZFL),P(IU0,IT1,ZFL)],[(IU0/2,IT0/2),(IU1/2,IT0/2),(IU1/2,IT1/2),(IU0/2,IT1/2)],uvl=uvl)
o=newobj('CCM office striped carpet (na)',bm,[M_CARP])
bm=bmesh.new(); uvl=bm.loops.layers.uv.verify(); T=0.6096
f=quad_uv(bm,[P(IU0,IT1,ZCE),P(IU1,IT1,ZCE),P(IU1,IT0,ZCE),P(IU0,IT0,ZCE)],[(IU0/T,IT1/T),(IU1/T,IT1/T),(IU1/T,IT0/T),(IU0/T,IT0/T)],uvl=uvl)
newobj('CCM office lay-in ceiling 2x2 ft grid (na)',bm,[M_CEIL])
bm=bmesh.new()
um=(IU0+IU1)/2
for (u,t) in ((um-0.95,-11.0),(um+0.95,-11.0),(um-0.95,-13.2),(um+0.95,-13.2)):
    box(bm,u-0.29,u+0.29,t+0.29,t-0.29,ZCE-0.006,ZCE-0.001)
newobj('CCM office 2x2 troffers (na, emissive)',bm,[M_TROF])
bm=bmesh.new()
box(bm,IU0+0.001,IU0+0.011,IT0-0.01,IT1+0.002,ZFL,ZCE)
box(bm,IU1-0.011,IU1-0.001,IT0-0.01,IT1+0.002,ZFL,ZCE)
box(bm,IU0+0.011,IU1-0.011,IT1+0.012,IT1+0.002,ZFL,ZCE)
fixnormals(bm); newobj('CCM office white wall skins (na)',bm,[M_WALL])
# base
bm=bmesh.new()
box(bm,IU0+0.011,IU0+0.02,IT0-0.02,IT1+0.012,ZFL,ZFL+0.10)
box(bm,IU1-0.02,IU1-0.011,IT0-0.02,IT1+0.012,ZFL,ZFL+0.10)
box(bm,IU0+0.02,IU1-0.02,IT1+0.021,IT1+0.012,ZFL,ZFL+0.10)
newobj('CCM office rubber cove base (na)',bm,[mats.get('MY_rubber_cove_base_dark_grey_UNVERIFIED') or M_KB])
# ---- 2. desks: wood tops on black steel legs, grey partitions, file pedestals ----
H=0.74; TH=0.03
desks=[]  # (u0,u1,t0,t1)
# A: run along the glass (users face the glass), 2 x 1.5 m
for k in range(2): desks.append((IU0+0.25+k*1.52,IU0+0.25+k*1.52+1.5,IT0-0.10,IT0-0.85))
# B: back-to-back pod at room centre/far side
for k in range(2): desks.append((IU1-1.65,IU1-0.15,-11.45-k*0.76,-11.45-k*0.76-0.75))
# C: run along the back wall
desks.append((IU0+0.25,IU0+1.75,IT1+0.85,IT1+0.10))
desks.append((IU0+1.77,IU0+2.57,IT1+0.85,IT1+0.10))
bt=bmesh.new(); bl=bmesh.new(); bp=bmesh.new(); bf=bmesh.new(); btr=bmesh.new()
for (u0,u1,t0,t1) in desks:
    box(bt,u0,u1,t0,t1,ZFL+H-TH,ZFL+H)
    for uu in (u0+0.05,u1-0.08):
        for tt in (t0-0.05,t1+0.08): box(bl,uu,uu+0.03,tt,tt-0.03,ZFL,ZFL+H-TH)
    box(bl,u0+0.08,u1-0.08,t1+0.12,t1+0.10,ZFL+H-0.12,ZFL+H-TH)  # modesty rail
    if u1-u0>1.0: box(bf,u1-0.50,u1-0.10,t0-0.25 if t0>t1 else t0+0.25,t1+0.15 if t0>t1 else t1-0.15,ZFL+0.01,ZFL+0.62)
# partitions: pod spine + pod ends, back-run divider, glass-run low screen between A and pod aisle
PH=1.22
def panel(u0,u1,t0,t1,z1):
    box(bp,u0,u1,t0,t1,ZFL+0.02,z1); box(btr,u0-0.005,u1+0.005,t0+0.004,t1-0.004,z1,z1+0.015)
panel(IU1-1.66,IU1-0.14,-12.19,-12.23,ZFL+PH)
panel(IU1-1.70,IU1-1.66,-11.40,-12.98,ZFL+1.05)
panel(IU0+0.25,IU0+2.57,IT1+0.88,IT1+0.86,ZFL+1.12)
panel(IU0+2.59,IU0+2.63,IT1+0.88,IT1+0.05,ZFL+1.12)
panel(IU0+3.06,IU0+3.10,IT0-0.10,IT0-0.90,ZFL+1.05)
fixnormals(bt)
newobj('CCM office wood-top desks (na)',bt,[M_WOOD])
newobj('CCM office desk legs + rails (na, black steel)',bl,[M_STEEL])
newobj('CCM office grey cubicle partitions (na)',bp,[M_PART])
newobj('CCM office partition top trim (na)',btr,[M_PTRIM])
newobj('CCM office file pedestals (na)',bf,[M_FILE])
# ---- 3. monitors (bezel + screen), keyboards ----
bb=bmesh.new(); bs=bmesh.new(); uvs=bs.loops.layers.uv.verify(); bk=bmesh.new()
def monitor(u,t,face_t,w=0.55,h=0.33,zb=ZFL+H+0.12):
    # face_t: +1 screen faces +t, -1 faces -t
    s=face_t
    box(bb,u-w/2,u+w/2,t,t-s*0.035,zb,zb+h)                         # bezel slab
    box(bb,u-0.03,u+0.03,t-s*0.05,t-s*0.08,ZFL+H,zb+0.05)            # stand neck
    box(bb,u-0.12,u+0.12,t-s*0.0,t-s*0.20,ZFL+H,ZFL+H+0.012)         # foot
    tt=t+s*0.002
    pts=[P(u-w/2+0.015,tt,zb+0.015),P(u+w/2-0.015,tt,zb+0.015),P(u+w/2-0.015,tt,zb+h-0.015),P(u-w/2+0.015,tt,zb+h-0.015)]
    if s<0: pts=[pts[1],pts[0],pts[3],pts[2]]
    ox=random.random()*0.5
    quad_uv(bs,pts,[(ox,0),(ox+0.5,0),(ox+0.5,1),(ox,1)] if s>0 else [(ox+0.5,0),(ox,0),(ox,1),(ox+0.5,1)],uvl=uvs)
    box(bk,u-0.22,u+0.22,t+s*0.30,t+s*0.15,ZFL+H,ZFL+H+0.02)
random.seed(30)
# A run users face +t (glass) -> screens face -t (toward users), monitors near glass edge
for (u0,u1,t0,t1) in desks[:2]:
    um_=(u0+u1)/2; monitor(um_-0.30,t0-0.18,-1); monitor(um_+0.30,t0-0.18,-1)
# pod: first desk users face +t? pod desk 0 (t -11.45..-12.20) users sit on +t side facing -t -> screens face +t at spine
pu=(desks[2][0]+desks[2][1])/2
monitor(pu-0.3,-12.13,1); monitor(pu+0.35,-12.13,1)
monitor(pu,-12.29,-1)
# back run: users face -t (wall) -> screens face +t
monitor(IU0+0.75,IT1+0.20,1); monitor(IU0+1.35,IT1+0.20,1); monitor(IU0+2.15,IT1+0.20,1,w=0.62,h=0.36)
fixnormals(bb); fixnormals(bk)
newobj('CCM office monitor bezels + stands (na)',bb,[M_BEZ])
newobj('CCM office monitor screens (na, generic content)',bs,[M_SCR])
newobj('CCM office keyboards (na)',bk,[M_KB])
# ---- 4. painting on the far (high-u) wall, lateral file + printer, totes, boxes, bins, plants ----
bm=bmesh.new(); uvl=bm.loops.layers.uv.verify(); uw=IU1-0.04; tc=-11.9; zc=ZFL+1.78; hw=0.55; hh=0.68
uw2=uw-0.003
quad_uv(bm,[P(uw2,tc+hw,zc-hh),P(uw2,tc-hw,zc-hh),P(uw2,tc-hw,zc+hh),P(uw2,tc+hw,zc+hh)],[(0,0),(1,0),(1,1),(0,1)],uvl=uvl)
newobj('CCM office abstract painting (na, generic, NOT the real artwork)',bm,[M_PAINT])
bm=bmesh.new(); box(bm,uw,IU1-0.012,tc+hw,tc-hw,zc-hh,zc+hh); newobj('CCM office painting canvas edge (na)',bm,[M_FRAME])
# lateral file + printer in far corner by the back wall (u high, t near back)
fu0,fu1=IU1-0.92,IU1-0.05; ft0,ft1=IT1+1.30,IT1+0.85
bm=bmesh.new(); box(bm,fu0,fu1,IT1+0.50,IT1+0.05,ZFL,ZFL+0.72)
for z in (ZFL+0.36,): box(bm,fu0-0.0,fu1,IT1+0.505,IT1+0.495,z-0.005,z+0.005)
newobj('CCM office lateral file cabinet (na)',bm,[M_FILE])
bm=bmesh.new(); box(bm,fu0+0.20,fu0+0.65,IT1+0.47,IT1+0.08,ZFL+0.72,ZFL+1.06); box(bm,fu0+0.24,fu0+0.61,IT1+0.47,IT1+0.30,ZFL+1.06,ZFL+1.12)
newobj('CCM office laser printer (na)',bm,[M_PRN])
bm=bmesh.new()
for k in range(2): box(bm,IU0+2.75,IU0+3.30,IT1+0.45,IT1+0.05,ZFL+k*0.33,ZFL+k*0.33+0.32)
newobj('CCM office storage totes (na)',bm,[M_TOTE])
bm=bmesh.new()
box(bm,IU0+2.72,IU0+3.30,IT1+0.48,IT1+0.06,ZFL+0.66,ZFL+0.98)
box(bm,IU0+2.78,IU0+3.25,IT1+0.44,IT1+0.08,ZFL+0.98,ZFL+1.26)
box(bm,fu0+0.70,fu1,IT1+0.48,IT1+0.06,ZFL+0.72,ZFL+0.95)
newobj('CCM office cardboard boxes (na)',bm,[M_BOX])
# bins (near the camera end, low-u side by the glass run) as 12-gon open-top cylinders
def cyl(bm,u,t,r0,r1,z0,z1,nseg=12):
    c=P(u,t,0)
    lo=[bm.verts.new(c+Vector((r0*math.cos(2*math.pi*k/nseg),r0*math.sin(2*math.pi*k/nseg),z0))) for k in range(nseg)]
    hi=[bm.verts.new(c+Vector((r1*math.cos(2*math.pi*k/nseg),r1*math.sin(2*math.pi*k/nseg),z1))) for k in range(nseg)]
    bm.faces.new(lo[::-1])
    for k in range(nseg): bm.faces.new([lo[k],lo[(k+1)%nseg],hi[(k+1)%nseg],hi[k]])
bm=bmesh.new(); cyl(bm,IU0+0.22,IT0-1.15,0.15,0.18,ZFL,ZFL+0.48); newobj('CCM office recycling bin (na, blue)',bm,[M_BLUEB])
bm=bmesh.new(); cyl(bm,IU0+0.22,IT0-1.55,0.15,0.18,ZFL,ZFL+0.48); newobj('CCM office trash bin (na)',bm,[M_BLKB])
bp_=bmesh.new(); bl_=bmesh.new()
random.seed(5)
def plant(u,t,h):
    cyl(bp_,u,t,0.13,0.17,ZFL,ZFL+0.35)
    c=P(u,t,ZFL+0.33)
    for k in range(14):
        a=random.uniform(0,2*math.pi); el=random.uniform(0.25,1.2); ln=random.uniform(0.45,h)
        dirv=Vector((math.cos(a)*math.cos(el),math.sin(a)*math.cos(el),math.sin(el)))
        side=Vector((-math.sin(a),math.cos(a),0))*random.uniform(0.05,0.10)
        tip=c+dirv*ln; mid=c+dirv*ln*0.5
        v=[bl_.verts.new(x) for x in (c,mid+side,tip,mid-side)]
        bl_.faces.new(v)
plant(IU0+0.20,IT0-0.25,0.85); plant(IU0+3.30,IT0-0.25,0.75); plant(IU1-1.95,-11.75,0.55)
newobj('CCM office planters (na)',bp_,[M_POT]); newobj('CCM office plants (na, low-poly fronds)',bl_,[M_LEAF])
# ---- 5. task chairs: instance the hidden mx chair proto via the mx GN group ----
chair=bpy.data.objects.get('MX proto task chair (hidden, instanced)'); ng=bpy.data.node_groups.get('MX_instance_proto_rot')
pts=[]
for (u0,u1,t0,t1) in desks[:2]: pts.append(((u0+u1)/2,t1-0.45,(0,1)))
pts.append((pu,-11.45+0.45,(0,-1))); pts.append((pu,-12.95-0.45,(0,1)))
pts.append((IU0+1.0,IT1+1.30,(0,-1))); pts.append((IU0+2.15,IT1+1.30,(0,-1)))
me=bpy.data.meshes.new('NA chair points'); vs=[]; rots=[]
random.seed(11)
for u,t,(fu,ft) in pts:
    vs.append(P(u,t,ZFL)); f=d*fu+n*ft; rots.append(math.atan2(f.y,f.x)+random.uniform(-0.4,0.4))
me.from_pydata(vs,[],[]); a=me.attributes.new('rot','FLOAT_VECTOR','POINT')
for i,r in enumerate(rots): a.data[i].vector=(0,0,r)
cp=bpy.data.objects.new('CCM office task chairs (na, GN instances of the mx proto)',me); col.objects.link(cp)
cp['msu_tag_session']=SES; cp['status']='UNVERIFIED'; cp['source']=SRC; cp['count']=len(pts)
if chair and ng:
    md=cp.modifiers.new('NA instances','NODES'); md.node_group=ng
    sid=[it.identifier for it in ng.interface.items_tree if getattr(it,'in_out','')=='INPUT' and it.socket_type=='NodeSocketObject'][0]
    md[sid]=chair
else: print("WARN no chair proto")
print("NEWOBJ",len(col.objects),"HIDDEN",hidden)
print("ROOM u",IU0,IU1,"t",IT0,IT1)
for nm,(u,t,z) in {'cam_photo':(IU0+0.35,IT1+0.45,ZFL+1.70),'tgt_photo':(IU1-0.2,-11.3,ZFL+0.9),'room_c':((IU0+IU1)/2,-12.0,ZFL+1.5)}.items():
    p=P(u,t,z); print("PT",nm,"%.2f,%.2f,%.2f"%tuple(p))
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/na/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))

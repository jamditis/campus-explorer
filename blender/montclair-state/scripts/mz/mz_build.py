# Session mz (Oct 30 2026, ~2:20 AM ET): NJ PBS studio detail pass 3 (Joe's Oct 29 10:45 PM correction follow-up):
# finer pedestal + tripod cameras (replace the chunky mx blocks, which are hidden not deleted), prompter screen content
# (generic text lines), viewfinders + tally lights, ceiling wire cable tray with hangers + cable drop to the video wall,
# a yellow/black cable protector ramp over the camera cables, an orange extension cord coil (photo ccom_njpbs_newsroom_21
# shows orange cords), IFB/mic packs + script pages on the anchor desk. Additive (new collection), all UNVERIFIED.
import bpy, bmesh, math, os
from mathutils import Vector
MODE=os.environ.get('MZ_MODE','TEST')
SES='mz'; COLN='MS_CCOM_newsroom_studio_detail3_20261030mz'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
Z=Vector((0,0,1))
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; UA=U0+0.35; ZF=137.41; ZC=146.4; TM=-9.8
mats=bpy.data.materials; HERE=os.path.dirname(bpy.data.filepath)
def mat(name,col,rough=0.6,metal=0.0,emit=None,es=0.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=es
    m['msu_tag_session']=SES; m['status']='UNVERIFIED'; return m
def imgmat(name,png,es,rough=0.25):
    m=mats.get(name)
    if m: return m
    im=bpy.data.images.load(os.path.join(HERE,'textures/mz',png),check_existing=True); im.pack()
    m=mats.new(name); m.use_nodes=True; N=m.node_tree.nodes; b=N['Principled BSDF']
    tx=N.new('ShaderNodeTexImage'); tx.image=im; tx.extension='EXTEND'
    m.node_tree.links.new(tx.outputs['Color'],b.inputs['Base Color']); m.node_tree.links.new(tx.outputs['Color'],b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value=es; b.inputs['Roughness'].default_value=rough
    m['msu_tag_session']=SES; m['status']='UNVERIFIED generic content, no real text/logos'; return m
M_CAM=mats['MX_studio_camera_body_dark_grey_UNVERIFIED']
M_HOOD=mat('MZ_prompter_hood_matte_black_UNVERIFIED',(0.012,0.012,0.013),0.75)
M_PED=mat('MZ_pedestal_column_satin_grey_UNVERIFIED',(0.16,0.16,0.17),0.35,metal=0.6)
M_RUB=mat('MZ_rubber_grip_black_UNVERIFIED',(0.02,0.02,0.02),0.85)
M_LENS=mat('MZ_lens_barrel_black_UNVERIFIED',(0.015,0.015,0.016),0.3,metal=0.2)
M_TAL=mat('MZ_tally_light_red_emit_UNVERIFIED',(0.8,0.02,0.02),0.3,emit=(1,0.05,0.03),es=6.0)
M_PRT=imgmat('MZ_prompter_text_lines_generic_UNVERIFIED','mz_prompter_text_lines_generic_UNVERIFIED.png',0.9,0.06)
M_VF=imgmat('MZ_viewfinder_generic_UNVERIFIED','mz_viewfinder_generic_UNVERIFIED.png',0.8)
M_TRAY=mat('MZ_cable_tray_galvanised_UNVERIFIED',(0.55,0.56,0.57),0.45,metal=0.85)
M_CAB=mats.get('MY_camera_cable_black_UNVERIFIED') or mat('MZ_cable_black',(0.012,0.012,0.012),0.45)
M_YEL=mat('MZ_cable_ramp_lid_safety_yellow_UNVERIFIED',(0.85,0.62,0.02),0.6)
M_RBK=mat('MZ_cable_ramp_body_black_UNVERIFIED',(0.02,0.02,0.02),0.8)
M_ORG=mat('MZ_extension_cord_orange_UNVERIFIED',(0.85,0.22,0.02),0.5)
M_PAP=mat('MZ_script_paper_white_UNVERIFIED',(0.85,0.85,0.83),0.8)
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
col['msu_tag_session']=SES
SRC="Joe correction Oct 29 10:45 PM + ref ccom_njpbs_newsroom_21 (pedestal/prompter cameras, tripod, octa softbox, orange cords, floor box; kind only)"
def newobj(name,bm,mlist,status='UNVERIFIED'):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']=status; o['source']=SRC; return o
def wbox(bm,c,ax,ay,hx,hy,z0,z1,mi=0):
    # box centred at world xy c, local axes ax/ay (unit, horizontal), half sizes, z range
    vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+Z*(zz-c.z)) for zz in (z0,z1) for sy in (-1,1) for sx in (-1,1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
def cyl(bm,a,b,r,seg=10,mi=0,caps=True):
    ax=(b-a); L_=ax.length; ax.normalize()
    ref=Z if abs(ax.dot(Z))<0.9 else d
    s=ax.cross(ref).normalized(); up=ax.cross(s).normalized()
    ra=[bm.verts.new(a+(s*math.cos(2*math.pi*k/seg)+up*math.sin(2*math.pi*k/seg))*r) for k in range(seg)]
    rb=[bm.verts.new(b+(s*math.cos(2*math.pi*k/seg)+up*math.sin(2*math.pi*k/seg))*r) for k in range(seg)]
    for k in range(seg): bm.faces.new([ra[k],ra[(k+1)%seg],rb[(k+1)%seg],rb[k]]).material_index=mi
    if caps:
        bm.faces.new(ra[::-1]).material_index=mi; bm.faces.new(rb).material_index=mi
def quad(bm,uvl,pts,mi=0,uvs=((0,0),(1,0),(1,1),(0,1))):
    f=bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index=mi
    for lp,uv in zip(f.loops,uvs): lp[uvl].uv=uv
    return f
def tube(bm,W,r,seg=6,mi=0):
    rings=[]
    for i,c in enumerate(W):
        a=(W[min(i+1,len(W)-1)]-W[max(i-1,0)]).normalized(); s=a.cross(Z).normalized()
        if s.length<0.5: s=d.copy()
        up=a.cross(s).normalized()
        rings.append([bm.verts.new(c+(s*math.cos(2*math.pi*j/seg)+up*math.sin(2*math.pi*j/seg))*r) for j in range(seg)])
    for A,B in zip(rings,rings[1:]):
        for j in range(seg): bm.faces.new([A[j],A[(j+1)%seg],B[(j+1)%seg],B[j]]).material_index=mi
# ---------- hide the chunky mx cameras (REVERT unhides) ----------
hidden=[]
for nm in ('CCOM newsroom studio cameras (mx)','CCOM newsroom prompter glass (mx)'):
    o=bpy.data.objects[nm]; o.hide_render=True; o.hide_viewport=True; hidden.append(nm)
bpy.context.scene['mz_hidden']=hidden
# ---------- 1. pedestal cameras (3) at the mx positions, lens toward -u (anchor desk) ----------
# mats: 0 body, 1 hood, 2 pedestal, 3 rubber, 4 lens, 5 tally
bmC=bmesh.new(); bmS=bmesh.new(); uvS=bmS.loops.layers.uv.new('UVMap')
def ped(u,t):
    c=P(u,t,ZF); f=-d; s=n
    def Q(du,dt,dz): return P(u+du,t+dt,ZF+dz)
    cyl(bmC,Q(0,0,0.06),Q(0,0,0.16),0.36,16,2)                    # base skirt
    for k in range(3):
        a=2*math.pi*k/3+0.5; cu,ct=0.29*math.cos(a),0.29*math.sin(a)
        tg=(-math.sin(a),math.cos(a))
        cyl(bmC,Q(cu-tg[0]*0.025,ct-tg[1]*0.025,0.05),Q(cu+tg[0]*0.025,ct+tg[1]*0.025,0.05),0.05,8,3)   # castors
    cyl(bmC,Q(0,0,0.16),Q(0,0,0.80),0.10,12,2)                    # column lower
    cyl(bmC,Q(0,0,0.80),Q(0,0,1.08),0.075,12,2)                   # column upper (telescoping)
    ring=[Q(0.30*math.cos(2*math.pi*k/24),0.30*math.sin(2*math.pi*k/24),0.66) for k in range(25)]
    tube(bmC,ring,0.013,6,3)                                      # steering ring
    for k in range(3):
        a=2*math.pi*k/3+1.0; cyl(bmC,Q(0.09*math.cos(a),0.09*math.sin(a),0.66),Q(0.29*math.cos(a),0.29*math.sin(a),0.66),0.008,6,2)
    cyl(bmC,Q(0,0,1.08),Q(0,0,1.18),0.11,12,0)                    # pan/tilt head
    wbox(bmC,Q(0.04,0,1.18),d,n,0.16,0.10,ZF+1.18,ZF+1.21,0)      # tilt plate
    wbox(bmC,Q(0.04,0,1.21),d,n,0.22,0.09,ZF+1.21,ZF+1.45,0)      # camera body
    wbox(bmC,Q(0.05,0,1.45),d,n,0.08,0.015,ZF+1.45,ZF+1.50,3)     # carry handle
    cyl(bmC,Q(-0.18,0,1.33),Q(-0.40,0,1.33),0.065,12,4)           # lens barrel
    # prompter hood: frustum from back (u-0.30) to front (u-0.68), open front; back plate
    bk=[Q(-0.30,-0.17,1.10),Q(-0.30,0.17,1.10),Q(-0.30,0.17,1.50),Q(-0.30,-0.17,1.50)]
    fr=[Q(-0.68,-0.24,1.02),Q(-0.68,0.24,1.02),Q(-0.68,0.24,1.58),Q(-0.68,-0.24,1.58)]
    B=[bmC.verts.new(p) for p in bk]; F=[bmC.verts.new(p) for p in fr]
    for i in range(4): bmC.faces.new([B[i],B[(i+1)%4],F[(i+1)%4],F[i]]).material_index=1
    bmC.faces.new(B[::-1]).material_index=1
    wbox(bmC,Q(-0.49,0,0.99),d,n,0.17,0.21,ZF+0.97,ZF+1.04,1)     # prompter monitor tray under the hood
    wbox(bmC,Q(-0.60,0,1.58),d,n,0.02,0.03,ZF+1.58,ZF+1.61,5)     # tally lamp on the hood top
    # prompter content plane (faces the talent, -u side), just inside the hood mouth
    quad(bmS,uvS,[Q(-0.665,0.215,1.05),Q(-0.665,-0.215,1.05),Q(-0.665,-0.215,1.55),Q(-0.665,0.215,1.55)],0)
    # viewfinder (rear, operator side +u) + screen
    wbox(bmC,Q(0.33,0,1.52),d,n,0.06,0.10,ZF+1.45,ZF+1.60,0)
    quad(bmS,uvS,[Q(0.392,-0.085,1.465),Q(0.392,0.085,1.465),Q(0.392,0.085,1.585),Q(0.392,-0.085,1.585)],1)
    wbox(bmC,Q(0.33,0,1.61),d,n,0.07,0.11,ZF+1.60,ZF+1.62,1)      # viewfinder sun hood top
    # pan bars (2) back + down to the operator, with rubber grips and zoom/focus thumb controls
    for sg in (-1,1):
        a=Q(0.12,sg*0.11,1.27); b=Q(0.78,sg*0.30,1.06); g=a.lerp(b,0.78)
        cyl(bmC,a,g,0.013,8,2); cyl(bmC,g,b,0.019,8,3)
        cyl(bmC,b,b+(b-a).normalized()*0.06,0.03,8,0)
for t in (-4.6,-6.2,-7.8): ped(UA+6.3,t)
# ---------- 2. tripod camera (u UA+7.4, t -2.9), aimed at the set ----------
u,t=UA+7.4,-2.9
def Qt(du,dt,dz): return P(u+du,t+dt,ZF+dz)
for a in range(3):
    ang=2*math.pi*a/3+0.3; du,dt=0.55*math.cos(ang),0.55*math.sin(ang)
    foot=Qt(du,dt,0.0); top=Qt(du*0.12,dt*0.12,1.15); mid=foot.lerp(top,0.45)
    cyl(bmC,foot,mid,0.017,6,2); cyl(bmC,mid,top,0.013,6,2)       # 2-stage leg
    cyl(bmC,Qt(du*0.30,dt*0.30,0.05),Qt(0,0,0.05),0.008,6,2)      # ground spreader arm
    wbox(bmC,foot+Z*0.0,d,n,0.03,0.03,ZF,ZF+0.02,3)               # rubber foot
cyl(bmC,Qt(0,0,1.13),Qt(0,0,1.22),0.075,12,0)                     # fluid head
wbox(bmC,Qt(0,0,1.22),d,n,0.19,0.075,ZF+1.22,ZF+1.40,0)           # camcorder body
wbox(bmC,Qt(0.0,0,1.40),d,n,0.10,0.012,ZF+1.40,ZF+1.46,3)         # top handle
cyl(bmC,Qt(-0.19,0,1.31),Qt(-0.36,0,1.31),0.05,10,4)              # lens
wbox(bmC,Qt(-0.39,0,1.31),d,n,0.03,0.07,ZF+1.25,ZF+1.37,1)        # lens hood
wbox(bmC,Qt(-0.12,0.12,1.37),d,n,0.05,0.008,ZF+1.33,ZF+1.41,0)    # flip-out LCD
quad(bmS,uvS,[Qt(-0.16,0.129,1.335),Qt(-0.08,0.129,1.335),Qt(-0.08,0.129,1.405),Qt(-0.16,0.129,1.405)],1)
wbox(bmC,Qt(-0.12,0,1.41),d,n,0.015,0.015,ZF+1.40,ZF+1.415,5)     # tally
cyl(bmC,Qt(0.12,0.02,1.24),Qt(0.40,0.42,1.04),0.012,8,2)           # pan bar (toward the window aisle, clear of the U desks)
newobj('CCOM newsroom pedestal + tripod cameras (mz, finer)',bmC,[M_CAM,M_HOOD,M_PED,M_RUB,M_LENS,M_TAL])
newobj('CCOM newsroom prompter + viewfinder screens (mz, generic)',bmS,[M_PRT,M_VF],'generic content, no real text; UNVERIFIED')
# ---------- 3. ceiling wire cable tray along the back of the studio + hangers + drop to the video wall ----------
bm=bmesh.new(); TT0,TT1=-9.40,-9.10; ZT=145.95; u0,u1=-17.25,1.30
for tt in (TT0,TT1):
    wbox(bm,P((u0+u1)/2,tt,0),d,n,(u1-u0)/2,0.003,ZT,ZT+0.06)     # side wires/rails
wbox(bm,P(u0+0.003,(TT0+TT1)/2,0),d,n,0.003,0.15,ZT,ZT+0.06)      # end cap
uu=u0+0.05
while uu<u1:
    wbox(bm,P(uu,(TT0+TT1)/2,0),d,n,0.004,0.15,ZT,ZT+0.008); uu+=0.20   # cross wires
uu=u0+0.4
while uu<u1:
    for tt in (TT0-0.02,TT1+0.02): cyl(bm,P(uu,tt,ZT-0.02),P(uu,tt,ZC),0.005,6)   # threaded rods
    wbox(bm,P(uu,(TT0+TT1)/2,0),d,n,0.02,0.18,ZT-0.04,ZT-0.005)   # trapeze strut
    uu+=1.5
newobj('CCOM newsroom ceiling wire cable tray + hangers (mz)',bm,[M_TRAY])
bm=bmesh.new()
for k,(dt,dz) in enumerate(((-0.07,0.015),(-0.02,0.02),(0.04,0.017),(0.08,0.022),(0.0,0.04))):
    tt=-9.25+dt; z=ZT+0.008+dz; r=0.011 if k<4 else 0.016
    W=[P(u1-0.1,tt,z),P(u0+0.25,tt,z),P(u0+0.12,tt,z-0.05),P(u0+0.10,tt,z-0.4)]
    W+= [P(u0+0.10+0.0,tt,zz) for zz in (144.0,142.0)]+[P(-17.45,-9.25+dt*0.5,141.30),P(-17.60,-9.25+dt*0.5,141.12),P(-17.655,-9.25+dt*0.5,141.0)]
    tube(bm,W,r,6)
newobj('CCOM newsroom tray cables + drop to video wall (mz)',bm,[M_CAB])
# ---------- 4. cable protector ramp over the 4 camera cables near the floor box ----------
bm=bmesh.new()
def ramp(ua,ub,ta,tb):
    tm=(ta+tb)/2; h=0.045
    prof=[(ta,0.0),(tm-0.07,h),(tm+0.07,h),(tb,0.0)]
    V=[[bm.verts.new(P(uu,tq,ZF+0.0015+z)) for tq,z in prof] for uu in (ua,ub)]
    for i in range(3): bm.faces.new([V[0][i],V[0][i+1],V[1][i+1],V[1][i]]).material_index=(0 if i==1 else 1)
    bm.faces.new([V[0][0],V[0][1],V[0][2],V[0][3]][::-1]).material_index=1; bm.faces.new([V[1][0],V[1][1],V[1][2],V[1][3]]).material_index=1
for ua,ub in ((-11.22,-10.75),(-10.74,-10.27)): ramp(ua,ub,-9.08,-8.78)
newobj('CCOM newsroom cable protector ramp (mz)',bm,[M_YEL,M_RBK])
# ---------- 5. orange extension cord: run along the window-wall skirting to a coil, then to the tripod ----------
bm=bmesh.new(); r=0.0045; zc=ZF+r
cu,ct=-11.6,-1.15; pts=[]
pts+= [P(-6.5,-0.36,zc),P(-8.5,-0.37,zc),P(-10.4,-0.40,zc),P(-11.0,-0.55,zc),P(-11.25,-0.80,zc)]
for k in range(3*20+1):            # 3 loops, slightly drifting, stacked a few mm
    a=2*math.pi*k/20+1.2; rr=0.24+0.02*math.sin(k*0.7); pts.append(P(cu+rr*math.cos(a)+0.003*k,ct+rr*math.sin(a),zc+0.0085*(k/20)))
pts+= [P(-11.2,-1.7,zc),P(-10.8,-2.3,zc),P(-10.55,-2.70,zc)]
tube(bm,pts,r,6)
wbox(bm,P(-6.45,-0.37,0),d,n,0.05,0.025,ZF,ZF+0.05)                   # plug / floor outlet at the wall base
newobj('CCOM newsroom orange extension cord + coil (mz)',bm,[M_ORG])
# ---------- 6. anchor desk: IFB/mic belt packs + script pages ----------
bm=bmesh.new(); zt=138.51
for k,tt in enumerate((-5.4,-6.9)):
    wbox(bm,P(-15.62,tt,0),d,n,0.035,0.012,zt,zt+0.095,1)              # pack standing up
    cyl(bm,P(-15.62,tt+0.008,zt+0.095),P(-15.62,tt+0.008,zt+0.17),0.0025,5,1)   # antenna
    W=[P(-15.62,tt,zt+0.01),P(-15.72,tt+0.05,zt+0.004),P(-15.80,tt+0.08,zt-0.02),P(-15.82,tt+0.10,zt-0.25)]
    tube(bm,W,0.002,5,1)
    ang=0.12*(1 if k else -1); a2=d*math.cos(ang)+n*math.sin(ang); b2=-d*math.sin(ang)+n*math.cos(ang)
    for j in range(3): wbox(bm,P(-15.30+0.004*j,tt-0.35+0.006*j,0),a2,b2,0.149,0.105,zt+0.0005+0.0012*j,zt+0.0012+0.0012*j,0)
newobj('CCOM newsroom anchor desk IFB packs + scripts (mz)',bm,[M_PAP,M_RUB])
sc=bpy.context.scene
sc['mz_note']="mz: collection %s; hid mx chunky cameras + prompter glass (scene['mz_hidden'])"%COLN
print("NEWOBJ",len(col.objects),[o.name for o in col.objects])
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/mz/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))

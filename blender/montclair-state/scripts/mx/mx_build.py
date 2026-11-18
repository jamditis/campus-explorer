# Session mx (Oct 30 2026): (1) SW-corner south-face windows 078-081 -> 2 tall arched single-height studio windows
# with blackout roller shades (set video wall behind); (2) studio detail: instanced task chairs (GN), pedestal + tripod
# cameras, light stands with softboxes, grid spot fixtures, raised-floor tile grid. All UNVERIFIED.
import bpy, bmesh, math, os
from mathutils import Vector
MODE=os.environ.get('MX_MODE','TEST')
SES='mx'; COLN='MS_CCOM_newsroom_studio_detail_20261030mx'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; ZB,ZT=135.3,147.61; SILL,SPR,R=137.85,144.75,1.05
UA=U0+0.35; UB=1.8; TF=-0.32; TBACK=-14.3; ZF=137.41; ZC=146.4; TM=-9.8
mats=bpy.data.materials
def mat(name,col,rough=0.6,emit=None,es=6.0,metal=0.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=es
    m['msu_tag_session']=SES; return m
M_WALL=mats['Wall_SCM_precast']; M_FR=mats['Mullion_mahogany']; M_GL=mats['CCOM_atrium_glass_interior']
M_REV=mats.get('CCOM_win_reveal_stucco') or M_WALL; M_SILL=mats.get('CCOM_win_sill_cast_stone') or M_WALL
M_SHADE=mat('MX_blackout_roller_shade_UNVERIFIED',(0.035,0.035,0.04),0.9)
M_CHAIR=mat('MX_task_chair_black_mesh_UNVERIFIED',(0.02,0.02,0.022),0.7)
M_CAM=mat('MX_studio_camera_body_dark_grey_UNVERIFIED',(0.05,0.05,0.055),0.4,metal=0.3)
M_PROMPT=mat('MX_prompter_glass_dark_UNVERIFIED',(0.01,0.01,0.012),0.05)
M_STAND=mat('MX_light_stand_black_UNVERIFIED',(0.015,0.015,0.015),0.5,metal=0.5)
M_SOFT=mat('MX_softbox_diffuser_emit_UNVERIFIED',(0.95,0.95,0.95),0.6,emit=(1.0,0.98,0.95),es=4.0)
M_SPOT=mat('MX_grid_spot_fixture_black_UNVERIFIED',(0.02,0.02,0.02),0.4,metal=0.4)
M_SPOTL=mat('MX_grid_spot_lens_emit_UNVERIFIED',(1,0.95,0.85),0.3,emit=(1.0,0.93,0.82),es=20.0)
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
col['msu_tag_session']=SES
SRC="Joe correction Oct 29 10:45 PM + refs ccom_njpbs_newsroom_21 / ccom_x 20260923_njpbs_newsroom_interior / ccom_usgbc_exterior_03"
def newobj(name,bm,mlist,status='UNVERIFIED',c=None):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); (c or col).objects.link(o)
    o['msu_tag_session']=SES; o['status']=status; o['source']=SRC
    return o
def box(bm,u0,u1,t0,t1,z0,z1,mi=0,PP=None):
    PP=PP or P
    vs=[bm.verts.new(PP(u,t,z)) for z in (z0,z1) for t in (t0,t1) for u in (u0,u1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
# ---------- 1. south face (plane u=U0, facing -d) ----------
hidden=[]
for i in (78,79,80,81):
    for o in bpy.data.objects:
        if o.name.startswith('CCOM_win_%03d_'%i):
            o.hide_render=True; o.hide_viewport=True; hidden.append(o.name)
CEN=[-7.44-T0,-4.04-T0]   # old column centres (P-frame t)
TS0,TS1=-9.33-T0,0.0
w=bpy.data.objects['School of Communication and Media walls']; Mw=w.matrix_world
bm=bmesh.new(); bm.from_mesh(w.data); kill=[]
for f in bm.faces:
    ok=True
    for v in f.verts:
        p=Mw@v.co; u=d.dot(p); t=n.dot(p)-C0-T0
        if not (abs(u-U0)<0.03 and TS0-0.005<=t<=TS1+0.02 and 134.5<=p.z<=ZT+0.02): ok=False; break
    if ok: kill.append(f)
print("KILL south faces",len(kill)); bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(w.data); bm.free()
w['mx_note']="mx: %d south-face faces (t %.2f..%.2f at u %.2f) removed; replaced by 'CCOM newsroom south wall (mx)'"%(len(kill),TS0,TS1,U0)
def Q(u,t,z): return P(u,t,z)
NA=12; DEP=0.35
# south face sits in a ~2.4 m slot under the Morehead Hall eave (roof 144.5 at 0.23 m from the wall, probe4):
# tall FLAT-headed single-height windows, head 144.10 (below that eave), same sill as the west bay.
HEAD=144.10
def arch(tc,r=R): return [(tc-r,HEAD),(tc+r,HEAD)]
bm=bmesh.new()
def skin(u,ta,flip):
    def q(a):
        bm.faces.new([bm.verts.new(Q(u,t,z)) for t,z in (a[::-1] if flip else a)])
    edges=[ta]+[x for c in CEN for x in (c-R,c+R)]+[TS1]
    for i in range(0,len(edges),2): q([(edges[i],ZB),(edges[i+1],ZB),(edges[i+1],ZT),(edges[i],ZT)])
    for c in CEN:
        q([(c-R,ZB),(c+R,ZB),(c+R,SILL),(c-R,SILL)])
        ap=arch(c)
        for k in range(len(ap)-1):
            (ta_,za),(tb,zb)=ap[k],ap[k+1]
            q([(ta_,za),(tb,zb),(tb,ZT),(ta_,ZT)])
skin(U0,TS0,False); skin(U0+DEP,TS0,True)
for c in CEN:
    for ts in (c-R,c+R):
        bm.faces.new([bm.verts.new(Q(uu,ts,z)) for uu,z in ((U0,SILL),(U0+DEP,SILL),(U0+DEP,HEAD),(U0,HEAD))]).material_index=1
    ap=arch(c)
    for k in range(len(ap)-1):
        (ta_,za),(tb,zb)=ap[k],ap[k+1]
        bm.faces.new([bm.verts.new(Q(U0,ta_,za)),bm.verts.new(Q(U0,tb,zb)),bm.verts.new(Q(U0+DEP,tb,zb)),bm.verts.new(Q(U0+DEP,ta_,za))]).material_index=1
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0005)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
ow=newobj('CCOM newsroom south wall (mx)',bm,[M_WALL,M_REV],'2 tall flat-headed single-height windows (slot under the Morehead eave); south face not photographed -> UNVERIFIED')
# outer skin: normals should face -d (outward). Check one face.
bm=bmesh.new()
for c in CEN: box(bm,U0-0.06,U0+DEP-0.02,c-R-0.10,c+R+0.10,SILL-0.09,SILL-0.005)
newobj('CCOM newsroom south sills (mx)',bm,[M_SILL])
UG=U0+0.16
bm=bmesh.new()
for c in CEN:
    pts=[(c+R,SILL),(c-R,SILL)]+arch(c)
    bm.faces.new([bm.verts.new(Q(UG,t,z)) for t,z in pts])
newobj('CCOM newsroom south glass (mx)',bm,[M_GL])
bm=bmesh.new(); FW=0.06
def bx(t0,t1,u0,u1,z0,z1): box(bm,u0,u1,t0,t1,z0,z1)
for c in CEN:
    bx(c-R,c-R+0.08,UG-0.05,UG+0.05,SILL,HEAD); bx(c+R-0.08,c+R,UG-0.05,UG+0.05,SILL,HEAD)
    bx(c-R,c+R,UG-0.05,UG+0.05,SILL,SILL+0.10); bx(c-R,c+R,UG-0.05,UG+0.05,HEAD-0.10,HEAD)
    for j in (1,2,3):
        tj=c-R+2*R*j/4; bx(tj-FW/2,tj+FW/2,UG-0.04,UG+0.04,SILL+0.10,HEAD-0.10)
    for z in [SILL+0.10+k*((HEAD-SILL-0.20)/7) for k in range(1,7)]:
        bx(c-R+0.08,c+R-0.08,UG-0.04,UG+0.04,z-0.03,z+0.03)
newobj('CCOM newsroom south mullion grid (mx, maroon)',bm,[M_FR])
# blackout roller shades: lowered to just above the set video wall (top 141.01) so the lit ceiling still reads
ZSH=141.35; US=U0+0.25
bm=bmesh.new()
for c in CEN:
    vs=[bm.verts.new(Q(US,t,z)) for t,z in ((c-R+0.02,ZSH),(c+R-0.02,ZSH),(c+R-0.02,HEAD-0.01),(c-R+0.02,HEAD-0.01))]; bm.faces.new(vs)
    box(bm,US-0.015,US+0.015,c-R+0.03,c+R-0.03,ZSH-0.04,ZSH,PP=lambda u,t,z:Q(u,t,z))
newobj('CCOM newsroom south blackout shades (mx)',bm,[M_SHADE],'shades behind the anchor set; UNVERIFIED')
# studio low-u side wall: cut out the window zone (keep t TS0..TBACK)
sw=bpy.data.objects['CCOM newsroom studio side + back walls (mw)']
old_sw=sw.data; old_sw.use_fake_user=True
bm=bmesh.new()
box(bm,UA-0.2,UA,TS0,TBACK,ZF,ZC); box(bm,UB,UB+0.2,TF,TBACK,ZF,ZC); box(bm,UA-0.2,UB+0.2,TBACK,TBACK-0.2,ZF,ZC)
me=bpy.data.meshes.new('CCOM newsroom studio side + back walls (mx)'); bm.to_mesh(me); bm.free()
for m in old_sw.materials: me.materials.append(m)
sw.data=me; sw['mx_note']="mx: low-u side wall now starts at t %.2f; window zone wall = 'CCOM newsroom south wall (mx)' (old mesh kept as fake-user '%s')"%(TS0,old_sw.name)
# ---------- 2. detail ----------
# 2a chair prototype (local: faces +X), instanced with GN on a point cloud
protoc=bpy.data.collections.get('MX_protos_hidden')
if protoc is None:
    protoc=bpy.data.collections.new('MX_protos_hidden'); col.children.link(protoc)
protoc.hide_render=True; protoc.hide_viewport=True
def L3(x,y,z): return Vector((x,y,z))
def lbox(bm,x0,x1,y0,y1,z0,z1): box(bm,x0,x1,y0,y1,z0,z1,PP=lambda u,t,z:L3(u,t,z))
bm=bmesh.new()
lbox(bm,-0.24,0.24,-0.24,0.24,0.44,0.51)       # seat
lbox(bm,-0.27,-0.22,-0.22,0.22,0.58,1.02)      # back
lbox(bm,-0.24,-0.20,-0.04,0.04,0.46,0.62)      # back spine
lbox(bm,-0.025,0.025,-0.025,0.025,0.10,0.44)   # gas column
for a in range(5):
    ang=2*math.pi*a/5; c,s=math.cos(ang),math.sin(ang)
    vs=[]
    for (x,y) in ((0,-0.025),(0.32,-0.02),(0.32,0.02),(0,0.025)):
        for z in (0.05,0.09): vs.append(L3(x*c-y*s,x*s+y*c,z))
    V=[bm.verts.new(v) for v in vs]
    for f in [(0,2,4,6),(1,7,5,3),(0,1,3,2),(2,3,5,4),(4,5,7,6),(6,7,1,0)]:
        bm.faces.new([V[i] for i in f])
    lbox(bm,0.30*c-0.025,0.30*c+0.025,0.30*s-0.025,0.30*s+0.025,0.0,0.05)  # caster
for y in (-0.25,0.25): lbox(bm,-0.12,0.12,y-0.02,y+0.02,0.58,0.61)   # arm pads
chair=newobj('MX proto task chair (hidden, instanced)',bm,[M_CHAIR],c=protoc)
# chair positions (u,t,facing-vector in u/t)
UC=(UA+4.6+UB)/2+0.5; TCn=-5.2; uL,uR=UC-5.0,UC+5.0; tFr,tBk=-1.8,-8.6
pts=[]
for k in range(9): pts.append((uL+0.8+k*(uR-uL-1.6)/8, tBk+1.3, (0,-1)))
for s,fu in ((uL+1.3,-1),(uR-1.3,1)):
    for k in range(4): pts.append((s, tFr-0.6-k*(tFr-tBk-1.8)/3, (fu,0)))
for k in (-1.3,0,1.3):
    pts.append((UC+k, TCn+1.15,(0,-1))); pts.append((UC+k, TCn-1.15,(0,1)))
pts.append((UC-2.55,TCn,(1,0))); pts.append((UC+2.55,TCn,(-1,0)))
pts.append((UA+1.25,-5.6,(1,0))); pts.append((UA+1.25,-6.8,(1,0)))   # anchor chairs behind the desk (on riser)
import random; random.seed(30)
me=bpy.data.meshes.new('MX chair points'); vs=[]; rots=[]
for u,t,(fu,ft) in pts:
    z=ZF+0.25 if u<UA+4.6 and -9.0<t<-3.5 else ZF
    vs.append(P(u,t,z)); f=d*fu+n*ft; rots.append(math.atan2(f.y,f.x)+random.uniform(-0.35,0.35))
me.from_pydata(vs,[],[])
a=me.attributes.new('rot','FLOAT_VECTOR','POINT')
for i,r in enumerate(rots): a.data[i].vector=(0,0,r)
cp=bpy.data.objects.new('CCOM newsroom task chairs (mx, GN instances)',me); col.objects.link(cp)
cp['msu_tag_session']=SES; cp['status']='UNVERIFIED'; cp['source']=SRC; cp['count']=len(pts)
ng=bpy.data.node_groups.get('MX_instance_proto_rot') 
if ng is None:
    ng=bpy.data.node_groups.new('MX_instance_proto_rot','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Proto',in_out='INPUT',socket_type='NodeSocketObject')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='ORIGINAL'
    na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT_VECTOR'; na.inputs['Name'].default_value='rot'
    io=N.new('GeometryNodeInstanceOnPoints')
    ng.links.new(gi.outputs[1],oi.inputs['Object']); ng.links.new(gi.outputs[0],io.inputs['Points'])
    ng.links.new(oi.outputs['Geometry'],io.inputs['Instance']); ng.links.new(na.outputs['Attribute'],io.inputs['Rotation'])
    ng.links.new(io.outputs['Instances'],go.inputs[0])
md=cp.modifiers.new('MX instances','NODES'); md.node_group=ng
sid=[it.identifier for it in ng.interface.items_tree if getattr(it,'in_out','')=='INPUT' and it.socket_type=='NodeSocketObject'][0]
md[sid]=chair
# 2b grid spot fixtures (proto + instances) over the set / studio
bm=bmesh.new(); lbox(bm,-0.11,0.11,-0.11,0.11,-0.32,0.0)  # yoke+can (pointing down)
lbox(bm,-0.13,0.13,-0.015,0.015,-0.05,0.02)
spot=newobj('MX proto grid spot (hidden, instanced)',bm,[M_SPOT],c=protoc)
bm=bmesh.new(); lbox(bm,-0.085,0.085,-0.085,0.085,-0.335,-0.32)
lens=newobj('MX proto grid spot lens (hidden, instanced)',bm,[M_SPOTL],c=protoc)
spts=[]
for t in (-2.5,-5.0,-7.5):
    for u in (UA+1.2,UA+2.6,UA+4.0,UA+5.4): spts.append(P(u,t,ZC-0.9))
for t in (-2.5,-7.5):
    for u in (UC-3,UC,UC+3): spts.append(P(u,t,ZC-0.9))
for nm,pr in (('CCOM newsroom grid spots (mx, GN instances)',spot),('CCOM newsroom grid spot lenses (mx, GN instances)',lens)):
    me=bpy.data.meshes.new(nm+' pts'); me.from_pydata(spts,[],[])
    a=me.attributes.new('rot','FLOAT_VECTOR','POINT')
    for i in range(len(spts)): a.data[i].vector=(0,0,math.atan2(d.y,d.x))
    o=bpy.data.objects.new(nm,me); col.objects.link(o); o['msu_tag_session']=SES; o['status']='UNVERIFIED'; o['source']=SRC
    m2=o.modifiers.new('MX instances','NODES'); m2.node_group=ng; m2[sid]=pr
# 2c studio cameras: 3 pedestal cameras with prompters aimed at the anchor desk + 1 tripod camera (photo)
bm=bmesh.new(); bmp=bmesh.new()
def cam_ped(u,t):
    box(bm,u-0.35,u+0.35,t-0.35,t+0.35,ZF+0.0,ZF+0.12)            # pedestal base
    box(bm,u-0.08,u+0.08,t-0.08,t+0.08,ZF+0.12,ZF+1.15)           # column
    box(bm,u-0.30,u+0.25,t-0.13,t+0.13,ZF+1.15,ZF+1.45)           # camera body (lens toward -u)
    box(bm,u-0.70,u-0.30,t-0.22,t+0.22,ZF+1.05,ZF+1.55)           # prompter hood
    box(bmp,u-0.705,u-0.70,t-0.18,t+0.18,ZF+1.09,ZF+1.51)         # prompter glass
    box(bm,u+0.25,u+0.75,t-0.015,t+0.015,ZF+1.25,ZF+1.28)         # pan bar
for t in (-4.6,-6.2,-7.8): cam_ped(UA+6.3,t)
# tripod camera (as in newsroom_21), near the U opening, aimed at the set
u,t=UA+7.4,-2.9
for a in range(3):
    ang=2*math.pi*a/3+0.3; du,dt=0.55*math.cos(ang),0.55*math.sin(ang)
    p0=P(u+du,t+dt,ZF); p1=P(u,t,ZF+1.25)
    ax=(p1-p0).normalized(); side=ax.cross(Vector((0,0,1))).normalized()*0.015; up=ax.cross(side).normalized()*0.015
    V=[bm.verts.new(p+s) for p in (p0,p1) for s in (side+up,side-up,-side-up,-side+up)]
    for f in [(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: bm.faces.new([V[i] for i in f])
box(bm,u-0.22,u+0.22,t-0.11,t+0.11,ZF+1.25,ZF+1.50); box(bm,u-0.36,u-0.22,t-0.06,t+0.06,ZF+1.31,ZF+1.43)
newobj('CCOM newsroom studio cameras (mx)',bm,[M_CAM])
newobj('CCOM newsroom prompter glass (mx)',bmp,[M_PROMPT])
# 2d light stands + octagonal softboxes either side of the set (photo: octa softbox on a wheeled stand)
bm=bmesh.new(); bms=bmesh.new()
def stand(u,t,aim_u,aim_t):
    for a in range(3):
        ang=2*math.pi*a/3; box(bm,u-0.02+0.25*math.cos(ang)/2-0.12*math.cos(ang),u+0.02+0.25*math.cos(ang),t-0.02+0.25*math.sin(ang)/2-0.12*math.sin(ang),t+0.02+0.25*math.sin(ang),ZF+0.04,ZF+0.08)
    box(bm,u-0.02,u+0.02,t-0.02,t+0.02,ZF,ZF+2.25)
    c=P(u,t,ZF+2.35); f=(d*(aim_u-u)+n*(aim_t-t)).normalized(); s=f.cross(Vector((0,0,1))).normalized(); up=Vector((0,0,1))
    ring=[c+(s*math.cos(2*math.pi*k/8)+up*math.sin(2*math.pi*k/8))*0.45 for k in range(8)]
    back=c-f*0.30
    Vr=[bm.verts.new(p) for p in ring]; Vb=bm.verts.new(back)
    for k in range(8): bm.faces.new([Vr[k],Vr[(k+1)%8],Vb])
    Vf=[bms.verts.new(p+f*0.005) for p in ring]; bms.faces.new(Vf[::-1])
stand(UA+5.0,-2.6,UA+2.3,-6.2); stand(UA+5.0,-9.2,UA+2.3,-6.2)
newobj('CCOM newsroom light stands + softbox shells (mx)',bm,[M_STAND])
newobj('CCOM newsroom softbox diffusers (mx, emissive)',bms,[M_SOFT])
# 2e raised-access floor tile grid (60 cm tiles, photo) as a material on the mw floor + riser
fl=bpy.data.objects['CCOM newsroom studio floor (raised access, mw)']
m0=fl.data.materials[0]; mt=mats.get('MX_studio_raised_floor_tiles_UNVERIFIED')
if mt is None:
    mt=m0.copy(); mt.name='MX_studio_raised_floor_tiles_UNVERIFIED'; mt['msu_tag_session']=SES
    nt=mt.node_tree; N=nt.nodes; b=N['Principled BSDF']
    tc=N.new('ShaderNodeTexCoord'); mp=N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value=(0,0,-math.atan2(d.y,d.x))
    br=N.new('ShaderNodeTexBrick'); br.offset=0.0; br.squash=1.0
    br.inputs['Scale'].default_value=1.0; br.inputs['Brick Width'].default_value=0.6; br.inputs['Row Height'].default_value=0.6
    br.inputs['Mortar Size'].default_value=0.006; br.inputs['Mortar Smooth'].default_value=0.3
    br.inputs['Color1'].default_value=(0.47,0.48,0.48,1); br.inputs['Color2'].default_value=(0.40,0.41,0.41,1); br.inputs['Mortar'].default_value=(0.20,0.20,0.21,1)
    br.inputs['Bias'].default_value=0.0
    nt.links.new(tc.outputs['Object'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],br.inputs['Vector'])
    nt.links.new(br.outputs['Color'],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=0.35
fl.data.materials[0]=mt
rs=bpy.data.objects['CCOM newsroom set riser (mw)']; rs.data.materials[0]=mt
# ---------- 3. clear pre-existing Morehead eave/roof + downspout/gutter geometry that pokes into the studio volume ----------
# (visible inside since the bay became double-height; probe5). Bisect at the CCOM south wall plane, drop the inside part.
trim={}
UCUT=U0-0.01
def inbox(p): 
    u=d.dot(p); t=n.dot(p)-C0-T0
    return UCUT-1e-4<u<2.05 and -14.5<t<-0.02 and 136.0<p.z<148.2
for nm in ['Morehead Hall barrel tile eave course','Morehead Hall eave soffit + fascia + rafter tails','Morehead Hall hip + ridge cap tiles','Morehead Hall roof (LiDAR)','Downspouts (3f)','Gutters half-round (3f, Life/CCOM UNVERIFIED)']:
    o=bpy.data.objects[nm]; M=o.matrix_world; Mi=M.inverted()
    if o.data.users>1: o.data=o.data.copy()
    bm=bmesh.new(); bm.from_mesh(o.data)
    cand=[f for f in bm.faces if any(inbox(M@v.co) for v in f.verts)]
    geom=list({v for f in cand for v in f.verts})+list({e for f in cand for e in f.edges})+cand
    co=Mi@P(UCUT,-5,140); no=(Mi.to_3x3()@d).normalized()
    bmesh.ops.bisect_plane(bm,geom=geom,plane_co=co,plane_no=no)
    kill=[f for f in bm.faces if inbox(M@f.calc_center_median())]
    nf0=len(bm.faces); bmesh.ops.delete(bm,geom=kill,context='FACES')
    loose=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    trim[nm]=len(kill); o['mx_note']="mx: %d faces inside the CCOM NJ PBS studio volume removed (cut at the CCOM south wall plane)"%len(kill)
print("TRIM",trim)
bpy.context.scene['mx_trimmed']=list(trim.keys())
ms=mats['MW_studio_set_backdrop_blue_UNVERIFIED'].node_tree.nodes['Principled BSDF']; ms.inputs['Emission Strength'].default_value=1.6
sc=bpy.context.scene; sc['mx_hidden']=hidden
sc['mx_note']="mx: set video wall emission 6->1.6; floor+riser material MW_studio_raised_floor_grey_UNVERIFIED -> MX_studio_raised_floor_tiles_UNVERIFIED"
print("NEWOBJ",len(col.objects),len(protoc.objects),"HIDDEN",len(hidden),"CHAIRS",len(pts))
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/mx/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))

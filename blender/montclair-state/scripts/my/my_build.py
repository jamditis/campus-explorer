# Session my (Oct 30 2026, ~1:25 AM ET): NJ PBS studio detail pass 2: video-wall content, fascia TV + desk-monitor
# screen content (generic procedural images, no real logos), rubber cove skirting, camera floor cables + floor boxes,
# riser nosing. Additive only (new collection), all UNVERIFIED.
import bpy, bmesh, math, os
from mathutils import Vector
MODE=os.environ.get('MY_MODE','TEST')
SES='my'; COLN='MS_CCOM_newsroom_studio_detail2_20261030my'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; UA=U0+0.35; UB=1.8; TF=-0.32; TBACK=-14.3; ZF=137.41; TM=-9.8; TS0=-9.33-T0
UC=(UA+4.6+UB)/2+0.5; TCn=-5.2; uL,uR=UC-5.0,UC+5.0; tFr,tBk=-1.8,-8.6
mats=bpy.data.materials; HERE=os.path.dirname(bpy.data.filepath)
def imgmat(name,png,es):
    m=mats.get(name)
    if m: return m
    im=bpy.data.images.load(os.path.join(HERE,'textures/my',png),check_existing=True); im.pack()
    m=mats.new(name); m.use_nodes=True; N=m.node_tree.nodes; b=N['Principled BSDF']
    tx=N.new('ShaderNodeTexImage'); tx.image=im; tx.extension='EXTEND'
    m.node_tree.links.new(tx.outputs['Color'],b.inputs['Base Color']); m.node_tree.links.new(tx.outputs['Color'],b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value=es; b.inputs['Roughness'].default_value=0.25
    m['msu_tag_session']=SES; m['status']='UNVERIFIED generic content, not a real NJ PBS graphic'; return m
def mat(name,col,rough=0.6,metal=0.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    m['msu_tag_session']=SES; return m
M_VW=imgmat('MY_videowall_abstract_skyline_UNVERIFIED','my_videowall_abstract_skyline_UNVERIFIED.png',1.5)
M_TV=imgmat('MY_tv_atlas_generic_broadcast_UNVERIFIED','my_tv_atlas_generic_broadcast_UNVERIFIED.png',1.2)
M_MS=imgmat('MY_desk_monitor_screen_generic_UNVERIFIED','my_desk_monitor_screen_generic_UNVERIFIED.png',0.7)
M_BEZ=mat('MY_screen_bezel_black_UNVERIFIED',(0.01,0.01,0.012),0.5)
M_BASE=mat('MY_rubber_cove_base_dark_grey_UNVERIFIED',(0.05,0.05,0.055),0.8)
M_CAB=mat('MY_camera_cable_black_UNVERIFIED',(0.012,0.012,0.012),0.45)
M_FBX=mat('MY_floor_box_brushed_steel_UNVERIFIED',(0.45,0.45,0.46),0.35,metal=0.8)
M_NOS=mat('MY_riser_nosing_aluminium_UNVERIFIED',(0.6,0.6,0.62),0.3,metal=0.9)
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
col['msu_tag_session']=SES
SRC="Joe correction Oct 29 10:45 PM + refs ccom_njpbs_newsroom_* / ccom_x 20260923_njpbs_newsroom_interior (kind only; content generic)"
def newobj(name,bm,mlist,status='UNVERIFIED'):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']=status; o['source']=SRC; return o
def box(bm,u0,u1,t0,t1,z0,z1,mi=0):
    vs=[bm.verts.new(P(u,t,z)) for z in (z0,z1) for t in (t0,t1) for u in (u0,u1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
def quad(bm,uvl,pts,uvs,mi=0):
    f=bm.faces.new([bm.verts.new(p) for p in pts]); f.material_index=mi
    for lp,uv in zip(f.loops,uvs): lp[uvl].uv=uv
    return f
# 1. video wall content plane + bezel (wall front face u=UA+0.06, t -3.0..-9.4, z ZF+0.25..ZF+3.6). viewer faces -d, right=+t
bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap'); uu=UA+0.064; z0,z1=ZF+0.25,ZF+3.6
quad(bm,uvl,[P(uu,-9.4,z0),P(uu,-3.0,z0),P(uu,-3.0,z1),P(uu,-9.4,z1)],[(0,0),(1,0),(1,1),(0,1)])
newobj('CCOM newsroom video wall content (my, generic)',bm,[M_VW],'generic abstract skyline content, NOT a real NJ PBS graphic; UNVERIFIED')
bm=bmesh.new(); B=0.05
box(bm,UA+0.06,UA+0.08,-9.4-B,-3.0+B,z1,z1+B); box(bm,UA+0.06,UA+0.08,-9.4-B,-3.0+B,z0-0.0,z0+0.03)
box(bm,UA+0.06,UA+0.08,-9.4-B,-9.4,z0,z1); box(bm,UA+0.06,UA+0.08,-3.0,-3.0+B,z0,z1)
newobj('CCOM newsroom video wall bezel (my)',bm,[M_BEZ])
# 2. fascia TV row screens (TV front face t=TM+0.06; viewer faces -n, right=-u)
bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap'); tt=TM+0.063
for k in range(7):
    u=UA+1.4+k*(UB-UA-2.8)/6; a,b=k/7+0.002,(k+1)/7-0.002
    quad(bm,uvl,[P(u+0.59,tt,140.75),P(u-0.59,tt,140.75),P(u-0.59,tt,141.39),P(u+0.59,tt,141.39)],[(a,0),(b,0),(b,1),(a,1)])
newobj('CCOM newsroom fascia TV screens (my, generic)',bm,[M_TV],'generic broadcast-like content; UNVERIFIED')
# 3. desk monitor screens
bm=bmesh.new(); uvl=bm.loops.layers.uv.new('UVMap'); U4=[(0,0),(1,0),(1,1),(0,1)]
for k in range(9):
    u=uL+0.8+k*(uR-uL-1.6)/8; tt=tBk+0.253
    quad(bm,uvl,[P(u+0.25,tt,ZF+0.82),P(u-0.25,tt,ZF+0.82),P(u-0.25,tt,ZF+1.13),P(u+0.25,tt,ZF+1.13)],U4)
for s,sg in ((uL+0.25,1),(uR-0.25,-1)):
    for k in range(4):
        t=tFr-0.6-k*(tFr-tBk-1.8)/3; us=s+sg*0.018
        if sg>0: pts=[P(us,t-0.25,ZF+0.82),P(us,t+0.25,ZF+0.82),P(us,t+0.25,ZF+1.13),P(us,t-0.25,ZF+1.13)]
        else:    pts=[P(us,t+0.25,ZF+0.82),P(us,t-0.25,ZF+0.82),P(us,t-0.25,ZF+1.13),P(us,t+0.25,ZF+1.13)]
        quad(bm,uvl,pts,U4)
newobj('CCOM newsroom desk monitor screens (my, generic)',bm,[M_MS])
# 4. rubber cove skirting (10 cm) along the west wall inner face and the high-u side wall; riser aluminium nosing
bm=bmesh.new(); H=0.10
box(bm,UA+0.02,UB-0.02,-0.30,-0.335,ZF,ZF+H)                 # inside face of the west (window) wall
box(bm,UB-0.015,UB,TF,TM+0.06,ZF,ZF+H)                        # high-u side wall, studio part
box(bm,UA,UA+0.015,TS0,-9.05,ZF,ZF+H)                         # low-u side wall between set riser and offices
box(bm,UA+4.6,UA+4.62,-3.5,-9.0,ZF,ZF+0.06)                   # riser kick base
newobj('CCOM newsroom rubber cove base (my)',bm,[M_BASE])
bm=bmesh.new(); box(bm,UA+4.57,UA+4.625,-3.48,-9.02,ZF+0.235,ZF+0.255)
box(bm,UA,UA+4.625,-3.48,-3.525,ZF+0.235,ZF+0.255); box(bm,UA,UA+4.625,-9.02,-8.975,ZF+0.235,ZF+0.255)
newobj('CCOM newsroom set riser nosing (my)',bm,[M_NOS])
# 5. camera cables (pedestals + tripod) to floor boxes at the back glass line
def cr(p0,p1,p2,p3,s):
    s2,s3=s*s,s*s*s
    return 0.5*((2*p1)+(-p0+p2)*s+(2*p0-5*p1+4*p2-p3)*s2+(-p0+3*p1-3*p2+p3)*s3)
def cable(bm,ctrl,r=0.0065):
    ctrl=[Vector((u,t,0)) for u,t in ctrl]; ctrl=[ctrl[0]]+ctrl+[ctrl[-1]]; pts=[]
    for i in range(1,len(ctrl)-2):
        for k in range(8): pts.append(cr(ctrl[i-1],ctrl[i],ctrl[i+1],ctrl[i+2],k/8))
    pts.append(ctrl[-2]); W=[P(p.x,p.y,ZF+r) for p in pts]; rings=[]
    for i,c in enumerate(W):
        a=(W[min(i+1,len(W)-1)]-W[max(i-1,0)]).normalized(); s=a.cross(Vector((0,0,1))).normalized()
        rings.append([bm.verts.new(c+s*r*math.cos(2*math.pi*j/6)+Vector((0,0,r*math.sin(2*math.pi*j/6)))) for j in range(6)])
    for A,Bv in zip(rings,rings[1:]):
        for j in range(6): bm.faces.new([A[j],A[(j+1)%6],Bv[(j+1)%6],Bv[j]])
bm=bmesh.new(); fb=bmesh.new(); ends=[]
pu=UA+6.3
for i,t in enumerate((-4.6,-6.2,-7.8)):
    ue=UA+6.75+i*0.16
    ctrl=[(pu+0.30,t),(pu+0.55,t-0.25),(ue,t-0.6),(ue-0.05,(t-0.6+TM)/2),(ue,TM+0.35)]
    cable(bm,ctrl); ends.append((ue,TM+0.35))
ctrl=[(UA+7.4,-2.9),(UA+7.15,-3.4),(UA+7.1,-4.0),(UA+7.0,-5.4),(UA+7.15,-7.0),(UA+7.2,TM+0.38)]
cable(bm,ctrl,0.0055)
box(fb,UA+6.62,UA+7.34,TM+0.50,TM+0.22,ZF,ZF+0.012)   # one 4-port floor box where the cables drop
newobj('CCOM newsroom camera floor cables (my)',bm,[M_CAB])
newobj('CCOM newsroom floor boxes (my)',fb,[M_FBX])
sc=bpy.context.scene
sc['my_note']="my: additive only (collection %s); no existing object edited"%COLN
print("NEWOBJ",len(col.objects),[o.name for o in col.objects])
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/my/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))

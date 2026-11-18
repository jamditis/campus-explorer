# Session my: low-poly abstract people placeholders (seated at desks/anchor desk, 1 camera operator, 1 standing)
# instanced via GN (MX_instance_proto_rot). Clearly placeholders -> UNVERIFIED; easy to hide (child collection).
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
MODE=os.environ.get('MY_MODE','TEST'); SES='my'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; UA=U0+0.35; UB=1.8; ZF=137.41; UC=(UA+4.6+UB)/2+0.5; TCn=-5.2
par=bpy.data.collections['MS_CCOM_newsroom_studio_detail2_20261030my']
pc=bpy.data.collections.get('MY_people_placeholders')
if pc is None: pc=bpy.data.collections.new('MY_people_placeholders'); par.children.link(pc)
pc['note']='abstract low-poly people placeholders for scale/life; hide this collection for empty-studio shots; UNVERIFIED'
pr=bpy.data.collections.get('MY_protos_hidden')
if pr is None: pr=bpy.data.collections.new('MY_protos_hidden'); par.children.link(pr)
pr.hide_render=True; pr.hide_viewport=True
mats=bpy.data.materials
m=mats.get('MY_people_clothes_random_UNVERIFIED')
if m is None:
    m=mats.new('MY_people_clothes_random_UNVERIFIED'); m.use_nodes=True; N=m.node_tree.nodes; b=N['Principled BSDF']
    oi=N.new('ShaderNodeObjectInfo'); cr=N.new('ShaderNodeValToRGB'); E=cr.color_ramp; E.interpolation='CONSTANT'
    cols=[(0.03,0.04,0.07),(0.25,0.27,0.30),(0.08,0.12,0.22),(0.35,0.12,0.10),(0.55,0.55,0.52),(0.06,0.18,0.14)]
    while len(E.elements)<len(cols): E.elements.new(0.5)
    for i,c in enumerate(cols): E.elements[i].position=i/len(cols); E.elements[i].color=(*c,1)
    m.node_tree.links.new(oi.outputs['Random'],cr.inputs['Fac']); m.node_tree.links.new(cr.outputs['Color'],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=0.8; m['msu_tag_session']=SES
ms=mats.get('MY_people_skin_neutral_UNVERIFIED')
if ms is None:
    ms=mats.new('MY_people_skin_neutral_UNVERIFIED'); ms.use_nodes=True; b=ms.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(0.42,0.33,0.27,1); b.inputs['Roughness'].default_value=0.6; ms['msu_tag_session']=SES
def seg(bm,a,b,r0,r1,mi=0,k=8):
    a,b=Vector(a),Vector(b); ax=(b-a); Lz=ax.length
    R=ax.normalized().to_track_quat('Z','Y').to_matrix().to_4x4()
    res=bmesh.ops.create_cone(bm,cap_ends=True,segments=k,radius1=r0,radius2=r1,depth=Lz,matrix=Matrix.Translation((a+b)/2)@R)
    for f in {f for v in res['verts'] for f in v.link_faces}: f.material_index=mi
def head(bm,c,r=0.105):
    res=bmesh.ops.create_icosphere(bm,subdivisions=2,radius=r,matrix=Matrix.Translation(Vector(c)))
    for f in {f for v in res['verts'] for f in v.link_faces}: f.material_index=1
def mk(name,bm):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m); me.materials.append(ms)
    for p in me.polygons: p.use_smooth=True
    o=bpy.data.objects.new(name,me); pr.objects.link(o); o['msu_tag_session']=SES; o['status']='UNVERIFIED placeholder'; return o
# seated (faces +X, seat top z 0.51)
bm=bmesh.new()
seg(bm,(-0.06,0,0.53),(-0.09,0,1.05),0.17,0.19)                 # torso
seg(bm,(-0.09,0,1.05),(-0.09,0,1.13),0.05,0.05,1)               # neck
head(bm,(-0.07,0,1.24))
for y in (-0.10,0.10):
    seg(bm,(-0.02,y,0.55),(0.40,y,0.57),0.075,0.065)            # thigh
    seg(bm,(0.40,y,0.55),(0.43,y,0.08),0.055,0.045)             # shin
    seg(bm,(0.43,y,0.04),(0.56,y,0.04),0.045,0.045)             # shoe
for y in (-0.22,0.22):
    seg(bm,(-0.08,y,1.00),(0.06,y*0.95,0.78),0.05,0.045)        # upper arm
    seg(bm,(0.06,y*0.95,0.78),(0.34,y*0.7,0.80),0.042,0.036)     # forearm
    seg(bm,(0.34,y*0.7,0.80),(0.42,y*0.65,0.80),0.035,0.03,1)   # hand
seated=mk('MY proto seated person (hidden, instanced)',bm)
# standing (faces +X)
bm=bmesh.new()
for y in (-0.10,0.10):
    seg(bm,(0,y,0.05),(0,y,0.88),0.06,0.08); seg(bm,(0.0,y,0.03),(0.14,y,0.03),0.045,0.045)
seg(bm,(0,0,0.88),(0,0,1.44),0.17,0.20); seg(bm,(0,0,1.44),(0,0,1.52),0.05,0.05,1); head(bm,(0.01,0,1.62))
for y in (-0.23,0.23):
    seg(bm,(0,y,1.40),(0.03,y*1.05,1.10),0.05,0.045); seg(bm,(0.03,y*1.05,1.10),(0.06,y,0.84),0.042,0.036); seg(bm,(0.06,y,0.84),(0.07,y,0.76),0.035,0.03,1)
standing=mk('MY proto standing person (hidden, instanced)',bm)
ch=bpy.data.objects['CCOM newsroom task chairs (mx, GN instances)']; Mc=ch.matrix_world
cv=[Mc@v.co for v in ch.data.vertices]; cr_=[a.vector[2] for a in ch.data.attributes['rot'].data]
pick=[1,4,6,10,15,25,26]   # 3 back-run desks, 1 per side run, both anchors
ng=bpy.data.node_groups['MX_instance_proto_rot']
sid=[it.identifier for it in ng.interface.items_tree if getattr(it,'in_out','')=='INPUT' and it.socket_type=='NodeSocketObject'][0]
def inst(name,pts,rots,proto):
    me=bpy.data.meshes.new(name+' pts'); me.from_pydata(pts,[],[])
    a=me.attributes.new('rot','FLOAT_VECTOR','POINT')
    for i,r in enumerate(rots): a.data[i].vector=(0,0,r)
    o=bpy.data.objects.new(name,me); pc.objects.link(o); o['msu_tag_session']=SES; o['status']='UNVERIFIED placeholder'
    md=o.modifiers.new('MY instances','NODES'); md.node_group=ng; md[sid]=proto; return o
inst('CCOM newsroom seated people placeholders (my, GN instances)',[cv[i] for i in pick],[cr_[i] for i in pick],seated)
ang=lambda f: math.atan2(f.y,f.x)
sp=[P(UA+7.30,-6.2,ZF), P(UC+2.9,TCn+1.9,ZF)]
sr=[ang(-d), ang(-(n))+0.5]
inst('CCOM newsroom standing people placeholders (my, GN instances)',sp,sr,standing)
print("PEOPLE",len(pick),len(sp),"objs",len(bpy.data.objects))
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/my/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE')); print("SAVED",out)

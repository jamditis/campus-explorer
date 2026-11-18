"""ws25: Partridge Hall (TX massing) -> cream stucco + red-tile hip roof with deep eaves, per Joe's Nov 8 photo
(his photos override older data, Joe Nov 10). Saves main."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene
CN='WS25_Partridge_tile_hip_roof_stucco_JoePhoto_20261110ws25'
col=bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
if col.name not in sc.collection.children: sc.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o)

def mat(name, rgb, rough, noise=0.0, scale=3.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial'); b=nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value=rough
    nt.links.new(b.outputs[0],out.inputs[0])
    if noise>0:
        tc=nt.nodes.new('ShaderNodeTexCoord'); n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=6
        cr=nt.nodes.new('ShaderNodeValToRGB')
        cr.color_ramp.elements[0].color=(*[c*(1-noise) for c in rgb],1); cr.color_ramp.elements[1].color=(*[min(1,c*(1+noise)) for c in rgb],1)
        nt.links.new(tc.outputs['Object'],n.inputs['Vector']); nt.links.new(n.outputs['Fac'],cr.inputs['Fac']); nt.links.new(cr.outputs['Color'],b.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.08; bump.inputs['Distance'].default_value=0.01
        n2=nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=180; nt.links.new(tc.outputs['Object'],n2.inputs['Vector'])
        nt.links.new(n2.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],b.inputs['Normal'])
    else:
        b.inputs['Base Color'].default_value=(*rgb,1)
    return m
# colours: sunlit photo samples sRGB (188,173,173)/(196,180,176) -> linear
STUCCO=mat('WS25_Partridge_stucco_cream_JoePhoto',(0.53,0.44,0.41),0.88,0.07,2.5)
WFRAME=mat('WS25_Partridge_window_frame_white_JoePhoto',(0.72,0.71,0.68),0.45)
FASCIA=mat('WS25_Partridge_fascia_burgundy_JoePhoto',(0.20,0.025,0.022),0.55)
SOFFIT=mat('WS25_Partridge_soffit_stucco_JoePhoto',(0.40,0.33,0.31),0.9)
TILE=bpy.data.materials['PI_Feliciano_roof_tile_forced_UNVERIFIED']
CAP=bpy.data.materials['WS16_Barrel_tile_terracotta_plain']

# 1. recolour the TX frame (only this object)
fr=[o for o in bpy.data.objects if o.name.startswith('TX Partridge precast frame')][0]
for s in fr.material_slots:
    if s.material and s.material.name in ('TX_Partridge_brown_brick_UNVERIFIED','TX_Partridge_precast_concrete_UNVERIFIED'): s.link='OBJECT'; s.material=STUCCO
    elif s.material and s.material.name=='TX_Partridge_bronze_mullion_UNVERIFIED': s.link='OBJECT'; s.material=WFRAME
print('FRAME slots',[s.material.name for s in fr.material_slots])
scr=[o for o in bpy.data.objects if o.name.startswith('TX Partridge roof screens')][0]
scr.hide_render=True; scr.hide_viewport=True

# 2. footprint OBB (rotation from the west/south edges)
core=[o for o in bpy.data.objects if o.name.startswith('TX Partridge core')][0]
pts=[(core.matrix_world@v.co).xy for v in core.data.vertices]
th=math.atan2(-237.6+235.8, -99.4+70.3)  # south edge direction (pointing W)
th=math.atan2(235.8-237.6, -70.3+99.4)   # W->E along south edge
c,s_=math.cos(th),math.sin(th)
def to_l(p): return Vector(( p.x*c+p.y*s_, -p.x*s_+p.y*c))
def to_w(u,v): return Vector((u*c-v*s_, u*s_+v*c))
L=[to_l(p) for p in pts]
u0,u1=min(p.x for p in L),max(p.x for p in L); v0,v1=min(p.y for p in L),max(p.y for p in L)
print('OBB',round(math.degrees(th),2),round(u1-u0,2),round(v1-v0,2))
OH=1.0; ZE=158.15; FD=0.30; PITCH=math.radians(21)
U0,U1,V0,V1=u0-OH,u1+OH,v0-OH,v1+OH
W=(U1-U0)/2; RZ=ZE+W*math.tan(PITCH); UC=(U0+U1)/2
RV0,RV1=V0+W,V1-W
print('ridge z',round(RZ,2),'len',round(RV1-RV0,2))
def P(u,v,z): w=to_w(u,v); return Vector((w.x,w.y,z))
A,B,C,D=P(U0,V0,ZE),P(U1,V0,ZE),P(U1,V1,ZE),P(U0,V1,ZE)
R0,R1=P(UC,RV0,RZ),P(UC,RV1,RZ)
slopes=[('S',[A,B,R0],-90),('E',[B,C,R1,R0],0),('N',[C,D,R1],90),('W',[D,A,R0,R1],180)]
def mkobj(name,verts,faces,m,rotz=None,origin=None):
    me=bpy.data.meshes.new(name)
    if origin is None: origin=Vector((0,0,0))
    M=Matrix.Translation(origin)@(Matrix.Rotation(rotz,4,'Z') if rotz is not None else Matrix())
    Mi=M.inverted()
    me.from_pydata([Mi@v for v in verts],[],faces); me.update()
    o=bpy.data.objects.new(name,me); o.matrix_world=M; col.objects.link(o)
    me.materials.append(m)
    for p in me.polygons: p.use_smooth=False
    return o
for nm,vs,deg in slopes:
    # local frame: x along eave, y up-slope horizontal (texture projects on object XY)
    rot=th+math.radians(deg)+math.radians(90)
    cen=sum(vs,Vector())/len(vs)
    o=mkobj(f'WS25_Partridge_hip_roof_{nm}_tile_UNVERIFIED_pitch',vs,[list(range(len(vs)))],TILE,rot,Vector((cen.x,cen.y,ZE)))
    a=o.data.attributes.new('em_ringforce','FLOAT','FACE'); a.data[0].value=1.0
    # make normals point up
    if o.data.polygons[0].normal.z<0: o.data.flip_normals()
# 3. fascia band + soffit (ring)
iu0,iu1,iv0,iv1=u0+0.05,u1-0.05,v0+0.05,v1-0.05
outer=[P(U0,V0,0),P(U1,V0,0),P(U1,V1,0),P(U0,V1,0)]
inner=[P(iu0,iv0,0),P(iu1,iv0,0),P(iu1,iv1,0),P(iu0,iv1,0)]
verts=[];faces=[]
for i in range(4):
    j=(i+1)%4
    a,b=outer[i],outer[j]
    k=len(verts); verts+= [Vector((a.x,a.y,ZE-FD)),Vector((b.x,b.y,ZE-FD)),Vector((b.x,b.y,ZE+0.06)),Vector((a.x,a.y,ZE+0.06))]; faces.append([k,k+1,k+2,k+3])
fo=mkobj('WS25_Partridge_eave_fascia_burgundy_UNVERIFIED',verts,faces,FASCIA)
verts=[];faces=[]
for i in range(4):
    j=(i+1)%4
    k=len(verts); z=ZE-FD
    verts+=[Vector((outer[i].x,outer[i].y,z)),Vector((inner[i].x,inner[i].y,z)),Vector((inner[j].x,inner[j].y,z)),Vector((outer[j].x,outer[j].y,z))]; faces.append([k,k+1,k+2,k+3])
so=mkobj('WS25_Partridge_eave_soffit_UNVERIFIED',verts,faces,SOFFIT)
for p in so.data.polygons:
    pass
if so.data.polygons[0].normal.z>0: so.data.flip_normals()
# fill between soffit inner edge and the wall top (closes the gap down to the parapet top 158.1): vertical skirt in stucco
# 4. ridge + hip caps (half-round, r=0.13)
bm=bmesh.new()
def cap(p,q,r=0.13,n=8):
    d=(q-p); Ln=d.length; d.normalize()
    side=d.cross(Vector((0,0,1)));
    if side.length<1e-6: side=Vector((1,0,0))
    side.normalize(); up=side.cross(d).normalized()
    if up.z<0: up=-up
    rings=[]
    for t in (p,q):
        ring=[]
        for i in range(n+1):
            a=math.pi*i/n
            ring.append(bm.verts.new(t+side*math.cos(a)*r+up*(math.sin(a)*r*0.8)))
        rings.append(ring)
    for i in range(n): bm.faces.new([rings[0][i],rings[0][i+1],rings[1][i+1],rings[1][i]])
cap(R0,R1)
for e,R in ((A,R0),(B,R0),(C,R1),(D,R1)): cap(e,R)
me=bpy.data.meshes.new('WS25_Partridge_ridge_hip_caps_UNVERIFIED'); bm.to_mesh(me); bm.free()
co=bpy.data.objects.new(me.name,me); col.objects.link(co); me.materials.append(CAP)
for p in me.polygons: p.use_smooth=True
# 5. burgundy corbel brackets, 2 per corner under the soffit (photo shows paired brackets at corners; count/size UNVERIFIED)
bm=bmesh.new()
corn=[(u0,v0,-1,-1),(u1,v0,1,-1),(u1,v1,1,1),(u0,v1,-1,1)]
for (cu,cv,su,sv) in corn:
    for (du,dv) in ((0, -sv*1.2),(-su*1.2,0)):
        # bracket along the outward direction of each face meeting the corner
        bu,bv=cu+du,cv+dv
        out=(su,0) if du==0 else (0,sv)
        L=0.85; Wd=0.22; H=0.55
        z1=ZE-FD; z0=z1-H
        for (a,b) in ((0,0),):
            pass
        q=[]
        for (ox,oz) in ((0,z0),(0,z1),(L,z1),(L*0.35,z0)):
            for w in (-Wd/2,Wd/2):
                uu=bu+out[0]*ox+(w if out[0]==0 else 0); vv=bv+out[1]*ox+(w if out[1]==0 else 0)
                q.append(bm.verts.new(P(uu,vv,oz)))
        idx=[(0,2,4,6),(1,7,5,3),(0,1,3,2),(2,3,5,4),(4,5,7,6),(6,7,1,0)]
        for f in idx:
            try: bm.faces.new([q[i] for i in f])
            except ValueError: pass
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS25_Partridge_corner_brackets_burgundy_UNVERIFIED'); bm.to_mesh(me); bm.free()
bo=bpy.data.objects.new(me.name,me); col.objects.link(bo); me.materials.append(FASCIA)
print('BUILT',[o.name for o in col.objects])
bpy.ops.wm.save_mainfile()
print('SAVED')

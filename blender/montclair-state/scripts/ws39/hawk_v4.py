# ws38 Red Hawk pass 3: one smooth blended body (metaballs -> mesh -> voxel remesh), gripping talons, feather relief.
# Local frame identical to ws35/36 bronze object: origin at plinth base centre, faces +Y, plinth top ~0.56, rock top ~0.88.
import bpy,bmesh,math,random,os
from mathutils import Vector,Matrix
random.seed(38)
for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
sc=bpy.context.scene
# ---------- metaball body ----------
mb=bpy.data.metaballs.new('hawk_mb'); mb.resolution=0.03; mb.render_resolution=0.03; mb.threshold=0.6
mo=bpy.data.objects.new('hawk_mb',mb); sc.collection.objects.link(mo)
def E(c,r,s=(1,1,1),rot=None,typ='ELLIPSOID',st=2.0):
    e=mb.elements.new(); e.type=typ; e.co=c; e.radius=r*K; e.stiffness=st
    if typ=='ELLIPSOID': e.size_x,e.size_y,e.size_z=s
    elif typ=='CAPSULE': e.size_x=s[0]
    if rot: e.rotation=rot
K=float(os.environ.get('MBK','1.7'))
q=lambda deg,ax: Matrix.Rotation(math.radians(deg),4,ax).to_quaternion()
fw=q(-36,'X')
E((0,0.02,1.52),0.30,(0.55,0.60,1.0),fw)      # lower belly
E((0,0.16,1.80),0.34,(0.62,0.66,1.0),fw)      # chest
E((0,0.30,2.06),0.28,(0.62,0.70,0.95),fw)     # upper breast
E((0,0.41,2.24),0.18,(0.75,0.85,1.0),fw)      # neck
E((0.02,0.50,2.36),0.15,(0.85,1.15,0.80))     # head
E((0.02,0.56,2.42),0.09,(1.1,0.9,0.35))       # brow ridge
E((0,-0.10,1.36),0.16,(0.6,1.0,0.45),q(-30,'X'))  # rump into tail
for sx in (-1,1):
    E((sx*0.12,0.12,1.36),0.17,(0.55,0.7,1.0),q(-15,'X'))   # feathered thigh 'trousers'
    E((sx*0.20,0.10,2.10),0.14,(0.8,0.8,0.8))               # shoulder
    # wing arm as capsule chain from shoulder up/out (blends into body)
    sh=Vector((sx*0.22,0.05,2.15)); S=Vector((sx*1.0,0.15,0.95)).normalized()
    for t,r in ((0.12,0.13),(0.35,0.11),(0.58,0.095),(0.8,0.08),(0.97,0.065)):
        E(sh+S*1.05*t,r,(1.6,1.0,0.75),S.to_track_quat('X','Z'))
bpy.context.view_layer.objects.active=mo
dg=bpy.context.evaluated_depsgraph_get()
me=bpy.data.meshes.new_from_object(mo.evaluated_get(dg))
body=bpy.data.objects.new('hawk_body',me); sc.collection.objects.link(body)
bpy.data.objects.remove(mo,do_unlink=True)
bm=bmesh.new(); bm.from_mesh(me)
# ---------- hooked beak (sculpted into body before remesh) ----------
def cone(r1,r2,d,M,seg=12): bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r1,radius2=r2,depth=d,matrix=M)
cone(0.065,0.012,0.16,Matrix.Translation((0.02,0.66,2.33))@Matrix.Rotation(math.radians(-105),4,'X'))
cone(0.022,0.003,0.08,Matrix.Translation((0.02,0.735,2.275))@Matrix.Rotation(math.radians(-165),4,'X'),8)
bm.to_mesh(me); bm.free()
rm=body.modifiers.new('remesh','REMESH'); rm.mode='VOXEL'; rm.voxel_size=0.014; rm.adaptivity=0.0
sm=body.modifiers.new('smooth','SMOOTH'); sm.factor=0.6; sm.iterations=4
bpy.context.view_layer.objects.active=body
for m in list(body.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
# feather relief on body: displace along normals with a scaled, stretched voronoi-like pattern (scale-shaped bumps)
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
from mathutils import noise
for v in bm.verts:
    p=v.co
    if p.z<1.15: continue
    # overlapping scallops: cell distance in a frame stretched along the body (down-slope)
    c=noise.voronoi(Vector((p.x*14,p.y*14,p.z*9)),distance_metric='DISTANCE',exponent=2.5)[0][0]
    v.co+=v.normal*(0.010*min(c,1.0)-0.004)+v.normal*0.003*noise.noise(p*40)
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
# ---------- separate parts: rock, talons, feathers ----------
bm=bmesh.new()
bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1,matrix=Matrix.Translation((0,0.05,0.62))@Matrix.Diagonal((0.6,0.5,0.32,1)))
for v in bm.verts:
    if v.co.z>0.6: v.co+=v.normal*(0.05*noise.noise(v.co*4)+0.02*noise.noise(v.co*13))
    else: v.co.z=max(v.co.z,0.55)
RT=0.88
def rocktop(x,y):
    best=0.55
    for v in bm.verts:
        if abs(v.co.x-x)<0.06 and abs(v.co.y-y)<0.06: best=max(best,v.co.z)
    return best
def tube(pts,r0,r1,seg=10):
    # tapered tube along polyline
    rings=[]
    n=len(pts)
    for i,p in enumerate(pts):
        d=(pts[min(i+1,n-1)]-pts[max(i-1,0)]).normalized()
        a=d.orthogonal().normalized(); b=d.cross(a)
        r=r0+(r1-r0)*i/(n-1)
        rings.append([bm.verts.new(p+(a*math.cos(2*math.pi*k/seg)+b*math.sin(2*math.pi*k/seg))*r) for k in range(seg)])
    for A,B in zip(rings,rings[1:]):
        for k in range(seg): bm.faces.new((A[k],A[(k+1)%seg],B[(k+1)%seg],B[k]))
    bm.faces.new(rings[0][::-1]); tip=bm.verts.new(pts[-1]+(pts[-1]-pts[-2]).normalized()*r1)
    for k in range(seg): bm.faces.new((rings[-1][k],rings[-1][(k+1)%seg],tip))
def bez(p0,p1,p2,n=8): return [p0*(1-t)**2+p1*2*t*(1-t)+p2*t*t for t in [i/(n-1) for i in range(n)]]
for sx in (-1,1):
    ank=Vector((sx*0.13,0.20,RT+0.10))
    tube(bez(Vector((sx*0.14,0.13,1.24)),Vector((sx*0.14,0.18,1.1)),ank,6),0.042,0.034,10)   # scaled tarsus
    for a,L in ((-28,0.20),(0,0.23),(28,0.20)):
        d=Matrix.Rotation(math.radians(a),3,'Z')@Vector((0,1,0))
        p0=ank; tipxy=ank+d*L; zt=rocktop(tipxy.x,tipxy.y)
        p2=Vector((tipxy.x,tipxy.y,zt+0.012)); p1=(p0+p2)/2+Vector((0,0,0.05))
        tube(bez(p0,p1,p2,7),0.026,0.016,8)                          # toe hugging rock
        c0=p2; c2=c0+d*0.045+Vector((0,0,-0.07)); c1=c0+d*0.06
        tube(bez(c0,c1,c2,5),0.014,0.003,8)                          # curved talon gripping over edge
    hb=ank+Vector((0,-0.16,0)); zt=rocktop(hb.x,hb.y)
    p2=Vector((hb.x,hb.y,zt+0.012)); tube(bez(ank,(ank+p2)/2+Vector((0,0,0.03)),p2,6),0.024,0.016,8)
    tube(bez(p2,p2+Vector((0,-0.05,0)),p2+Vector((0,-0.03,-0.07)),5),0.013,0.003,8)   # hallux talon
# feathers (cards with rachis ridge and slight twist)
def feather(origin,dirv,nrm,Lg,wd,th=0.022):
    side=dirv.cross(nrm).normalized(); vs=[]
    for k in range(9):
        t=k/8; w=wd*(0.55+0.45*math.sin(math.pi*min(1,t*1.15)))*(1-t**4*0.85)
        c=origin+dirv*Lg*t+nrm*0.035*math.sin(math.pi*t)
        tw=Matrix.Rotation(math.radians(6*t),3,dirv)
        sd=tw@side; nn=tw@nrm
        vs.append([bm.verts.new(c+sd*w/2+nn*th*0.3),bm.verts.new(c+nn*th),bm.verts.new(c-sd*w/2+nn*th*0.3),bm.verts.new(c-sd*w/2-nn*th*0.3),bm.verts.new(c-nn*th*0.4),bm.verts.new(c+sd*w/2-nn*th*0.3)])
    for a,b in zip(vs,vs[1:]):
        for k in range(6): bm.faces.new((a[k],a[(k+1)%6],b[(k+1)%6],b[k]))
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
for sx in (-1,1):
    sh=Vector((sx*0.22,0.05,2.15)); S=Vector((sx*1.0,0.15,0.95)).normalized()
    D=Vector((sx*0.95,0,-1.0)).normalized()      # down-out, in the frontal plane: broad face to the road
    C=D*0.85+Vector((0,-1,0))*0.45; C=(C-S*C.dot(S)).normalized(); Nw=S.cross(C).normalized()
    if Nw.y<0: Nw=-Nw
    wr=sh+S*1.05
    for k in range(10):                                   # primaries, fingered tips
        a=math.radians(-4+k*8); d=(S*math.cos(a)+C*math.sin(a)).normalized()
        feather(wr-Nw*0.012*k,d,Nw,1.30-0.04*k,0.21)
    for k in range(10):                                   # secondaries
        t=k/9; o=sh.lerp(wr,0.12+0.88*t); d=(C*0.92+S*0.25*(1-t)).normalized()
        feather(o-Nw*0.02,d,Nw,0.86,0.24)
    for row,(L,wd,off) in enumerate(((0.48,0.19,0.03),(0.30,0.15,0.055))):   # two rows of coverts
        for k in range(12):
            t=k/11; o=sh.lerp(wr,0.04+0.92*t)+C*(0.03+0.03*row); d=(C*0.95+S*0.2).normalized()
            feather(o+Nw*off,d,Nw,L,wd)
for k in range(9):                                        # tail fan
    a=math.radians(-32+k*8); d=(Matrix.Rotation(a,3,'Y')@Vector((0,-0.55,-0.8))).normalized()
    feather(Vector((0,-0.14,1.30)),d,Vector((0,0.82,-0.55)).normalized(),0.64,0.13)
m2=bpy.data.meshes.new('hawk_parts'); bm.to_mesh(m2); bm.free()
parts=bpy.data.objects.new('hawk_parts',m2); sc.collection.objects.link(parts)
for p in m2.polygons: p.use_smooth=True
# join
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); parts.select_set(True)
bpy.context.view_layer.objects.active=body; bpy.ops.object.join()
body.name='RedHawk_bronze_v4_ws39'; body.data.name='RedHawk_bronze_v4_ws39'
body.modifiers.new('wn','WEIGHTED_NORMAL')
# bronze material with feather-relief bump + patina
M=bpy.data.materials.new('RedHawk_bronze_v3'); M.use_nodes=True; nt=M.node_tree; N=nt.nodes; Ln=nt.links
bs=N['Principled BSDF']; bs.inputs['Metallic'].default_value=0.85; bs.inputs['Roughness'].default_value=0.42
tc=N.new('ShaderNodeTexCoord'); mp=N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(14,14,9)
vo=N.new('ShaderNodeTexVoronoi'); vo.feature='DISTANCE_TO_EDGE'
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=30
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.35; bp.inputs['Distance'].default_value=0.01
Ln.new(tc.outputs['Object'],mp.inputs['Vector']); Ln.new(mp.outputs['Vector'],vo.inputs['Vector'])
mx=N.new('ShaderNodeMath'); mx.operation='ADD'
Ln.new(vo.outputs['Distance'],mx.inputs[0]); Ln.new(nz.outputs['Fac'],mx.inputs[1])
Ln.new(mx.outputs[0],bp.inputs['Height']); Ln.new(bp.outputs['Normal'],bs.inputs['Normal'])
cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.035,0.028,0.022,1); cr.color_ramp.elements[1].color=(0.11,0.075,0.045,1)
ao=N.new('ShaderNodeAmbientOcclusion')
Ln.new(nz.outputs['Fac'],cr.inputs['Fac']); Ln.new(cr.outputs['Color'],bs.inputs['Base Color'])
body.data.materials.append(M)
print('W39H verts',len(body.data.vertices))
out=os.environ.get('OUT','/workspace/nj-scenes/assets/redhawk_statue_v4_ws39.blend')
# preview scene (light): plinth, ground, sun, camera from road side 3/4 like Joe shot #4
if os.environ.get('PREVIEW')=='1':
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=0.85,depth=0.56,location=(0,0,0.28))
    pl=bpy.context.object; pm=bpy.data.materials.new('granite'); pm.use_nodes=True; pm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.45,0.44,0.42,1); pl.data.materials.append(pm)
    bpy.ops.mesh.primitive_plane_add(size=40); g=bpy.context.object; gm=bpy.data.materials.new('lawn'); gm.use_nodes=True; gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.12,0.22,0.06,1); g.data.materials.append(gm)
    sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sun.data.energy=4; sun.rotation_euler=(math.radians(55),0,math.radians(200)); sc.collection.objects.link(sun)
    w=bpy.data.worlds.new('w'); w.use_nodes=True; w.node_tree.nodes['Background'].inputs['Color'].default_value=(0.55,0.65,0.8,1); w.node_tree.nodes['Background'].inputs['Strength'].default_value=0.8; sc.world=w
    cd=bpy.data.cameras.new('c'); cd.lens=40; cam=bpy.data.objects.new('cam',cd); sc.collection.objects.link(cam); sc.camera=cam
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=32; sc.cycles.use_denoising=True
    sc.render.resolution_x=960; sc.render.resolution_y=720; sc.render.resolution_percentage=100
    for lab,loc in (('front34',(-3.2,6.2,1.6)),('profile',(6.5,1.0,1.7))):
        cam.location=loc; cam.rotation_euler=(Vector((0,0.1,1.85))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=f"/workspace/nj-scenes/montclair-state/renders/test/ws39_hawk_v4_{lab}.jpg"; sc.render.image_settings.file_format='JPEG'
        bpy.ops.render.render(write_still=True); print('W39H WROTE',sc.render.filepath)
    for o in (pl,g,sun,cam): bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=out); print('W39H SAVED',out)

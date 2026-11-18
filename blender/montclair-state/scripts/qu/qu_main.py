# qu (Nov 2 2026 ~11:30 PM ET, MAIN, day 7 Richardson Hall glass + interior hint). ALL UNVERIFIED, reversible:
# REVERT=1 -> pre-qu (QT_SIG 8063 819 4004 eba21278d9e9). QUSAVE=1 saves.
# (1) Richardson glass (ground storey, middle ribbon, top punched windows) -> QU_Richardson_glass_clear_bronze_UNVERIFIED:
#     fresnel mix of a bronze-tinted Transparent BSDF and a sharp Glossy, so you see into the building and the sky reflects at
#     grazing angles. Old material kept with a fake user; object prop qu_prev_glass.
# (2) QU_Richardson_interior_hint_UNVERIFIED: per storey a floor slab, a ceiling with emissive 0.6x1.2 m light panels,
#     a back (core) wall 5.5-7 m in, office partitions on the upper storeys and blinds at random drops behind the upper glass.
#     Interior layout is a generic guess (no interior photos).
# (3) camera QU_CAM_closeup_richardson_glass_interior.
import bpy,bmesh,json,math,os,random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
COL='QU_Richardson_interior_hint_UNVERIFIED'; GM='QU_Richardson_glass_clear_bronze_UNVERIFIED'
OLDG='QP_Richardson_glass_bronze_dark_UNVERIFIED'
MATS=[GM,'QU_int_ceiling_panels_UNVERIFIED','QU_int_wall_offwhite_UNVERIFIED','QU_int_floor_terrazzo_UNVERIFIED','QU_int_floor_carpet_UNVERIFIED','QU_int_blind_fabric_UNVERIFIED','QU_int_partition_UNVERIFIED']
OBJS=['QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_upper_block_UNVERIFIED']
def revert():
    og=bpy.data.materials.get(OLDG)
    for n in OBJS:
        o=bpy.data.objects.get(n)
        if not o: continue
        for s in o.material_slots:
            if s.material and s.material.name==GM: s.material=og
        if 'qu_prev_glass' in o: del o['qu_prev_glass']
    if og and og.get('qu_fake'): og.use_fake_user=False; del og['qu_fake']
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('QU_') and m.users==0]: bpy.data.meshes.remove(me)
    for c in [c for c in bpy.data.cameras if c.name.startswith('QU_CAM') and c.users==0]: bpy.data.cameras.remove(c)
    for m in [m for m in bpy.data.materials if (m.name in MATS or m.name.startswith('QU_')) and m.users==0 and not m.use_fake_user]:
        bpy.data.materials.remove(m)
    for d in [d for d in bpy.data.meshes if d.users==0 and d.name.startswith('KIT_')]: bpy.data.meshes.remove(d)
    print('QU reverted')
revert()
if REV:
    if os.environ.get('QUSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
EMI=float(os.environ.get('QU_EMI','5.0')); TR=float(os.environ.get('QU_TR','0.50'))
P=json.load(open('data/qu/interior_polys_qu.json'))
sc=bpy.context.scene
# ---------- materials
def newmat(name):
    m=bpy.data.materials.new(name); m.use_nodes=True; return m,m.node_tree.nodes,m.node_tree.links
g,N,L=newmat(GM); N.remove(N['Principled BSDF']); out=N['Material Output']
tr=N.new('ShaderNodeBsdfTransparent'); tr.inputs['Color'].default_value=(TR,TR*0.93,TR*0.82,1)
gl=N.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value=0.02; gl.inputs['Color'].default_value=(0.72,0.70,0.67,1)
fr=N.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value=1.52
ad=N.new('ShaderNodeMath'); ad.operation='MULTIPLY_ADD'; ad.use_clamp=True; L.new(fr.outputs[0],ad.inputs[0]); ad.inputs[1].default_value=1.2; ad.inputs[2].default_value=0.07
mx=N.new('ShaderNodeMixShader'); L.new(ad.outputs[0],mx.inputs[0]); L.new(tr.outputs[0],mx.inputs[1]); L.new(gl.outputs[0],mx.inputs[2]); L.new(mx.outputs[0],out.inputs['Surface'])
g['UNVERIFIED_qu']='tint/reflection a visual guess; real Richardson glazing type unknown'
# ceiling: off-white tile with emissive panels on a 2.4 x 3.0 m grid (world coords; objects have identity transforms)
c,N,L=newmat('QU_int_ceiling_panels_UNVERIFIED'); Pb=N['Principled BSDF']; Pb.inputs['Base Color'].default_value=(0.62,0.61,0.58,1); Pb.inputs['Roughness'].default_value=0.9
tc=N.new('ShaderNodeTexCoord'); sp=N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'],sp.inputs[0])
def M(op,a,b=None):
    n=N.new('ShaderNodeMath'); n.operation=op
    for i,v in enumerate((a,b)):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: L.new(v,n.inputs[i])
    return n.outputs[0]
def inpanel(v,pitch,half):  # 1 inside |frac(v/pitch)-0.5|*pitch < half
    d=M('MULTIPLY',M('ABSOLUTE',M('SUBTRACT',M('FRACT',M('DIVIDE',v,pitch)),0.5)),pitch); return M('LESS_THAN',d,half)
pan=M('MULTIPLY',inpanel(sp.outputs['X'],2.4,0.30),inpanel(sp.outputs['Y'],3.0,0.60))
L.new(pan,Pb.inputs['Emission Strength']); Pb.inputs['Emission Color'].default_value=(1.0,0.95,0.86,1)
ms=N.new('ShaderNodeMath'); ms.operation='MULTIPLY'; L.new(pan,ms.inputs[0]); ms.inputs[1].default_value=EMI; L.new(ms.outputs[0],Pb.inputs['Emission Strength'])
def flat(name,col,rough=0.8):
    m,N,L=newmat(name); b=N['Principled BSDF']; b.inputs['Base Color'].default_value=col; b.inputs['Roughness'].default_value=rough; return m
wall=flat('QU_int_wall_offwhite_UNVERIFIED',(0.55,0.53,0.49,1),0.85)
terr=flat('QU_int_floor_terrazzo_UNVERIFIED',(0.36,0.35,0.33,1),0.35)
carp=flat('QU_int_floor_carpet_UNVERIFIED',(0.10,0.105,0.12,1),0.95)
blind=flat('QU_int_blind_fabric_UNVERIFIED',(0.58,0.55,0.48,1),0.9)
part=flat('QU_int_partition_UNVERIFIED',(0.45,0.44,0.42,1),0.8)
# ---------- swap glass
og=bpy.data.materials[OLDG]
if not og.use_fake_user: og.use_fake_user=True; og['qu_fake']=1
nsw=0
for n in OBJS:
    o=bpy.data.objects[n]
    for s in o.material_slots:
        if s.material==og: s.material=g; nsw+=1
    o['qu_prev_glass']=OLDG
print('QU glass slots swapped',nsw)
# ---------- geometry
col=bpy.data.collections.new(COL); sc.collection.children.link(col)
def mkobj(name,bm,mat):
    me=bpy.data.meshes.new('QU_'+name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new('QU_'+name+'_UNVERIFIED',me); col.objects.link(o); o['UNVERIFIED_qu']='generic interior hint, no interior photos'; return o
def slab(ring,z,up,name,mat):
    bm=bmesh.new(); vs=[bm.verts.new((x,y,z)) for x,y in ring]; f=bm.faces.new(vs); f.normal_update()
    if (f.normal.z>0)!=up: f.normal_flip()
    bmesh.ops.triangulate(bm,faces=bm.faces[:]) if False else None
    return mkobj(name,bm,mat)
def band(ring,z0,z1,name,mat,outward=True):
    bm=bmesh.new(); n=len(ring); lo=[bm.verts.new((x,y,z0)) for x,y in ring]; hi=[bm.verts.new((x,y,z1)) for x,y in ring]
    ccw=sum(ring[i][0]*ring[(i+1)%n][1]-ring[(i+1)%n][0]*ring[i][1] for i in range(n))>0
    for i in range(n):
        j=(i+1)%n; q=[lo[i],lo[j],hi[j],hi[i]]
        bm.faces.new(q if ccw==outward else q[::-1])
    return mkobj(name,bm,mat)
random.seed(20261102)
def ring_samples(ring,step,jit=0.0):
    out=[];n=len(ring)
    for i in range(n):
        a=Vector(ring[i]); b=Vector(ring[(i+1)%n]); d=b-a; Ln=d.length
        if Ln<1.0: continue
        k=max(1,int(Ln//step)); 
        for t in range(k): out.append((a,b,(t+0.5)/k,Ln/k))
    return out
def blinds(ring,ztop,maxdrop,name,seg):
    bm=bmesh.new(); n=len(ring); cnt=0
    for i in range(n):
        a=Vector(ring[i]); b=Vector(ring[(i+1)%n]); Ln=(b-a).length
        if Ln<0.6: continue
        k=max(1,round(Ln/seg))
        for t in range(k):
            r=random.random()
            if r<0.30: continue
            drop=maxdrop*random.choice((0.15,0.3,0.45,0.6,0.85,1.0))
            p=a+(b-a)*(t/k); q=a+(b-a)*((t+1)/k)
            v=[bm.verts.new((p.x,p.y,ztop-drop)),bm.verts.new((q.x,q.y,ztop-drop)),bm.verts.new((q.x,q.y,ztop)),bm.verts.new((p.x,p.y,ztop))]
            bm.faces.new(v); cnt+=1
    print('QU blinds',name,cnt); return mkobj(name,bm,blind)
def partitions(slab_ring,depth,z0,z1,name,step):
    bm=bmesh.new(); n=len(slab_ring); cnt=0
    ccw=sum(slab_ring[i][0]*slab_ring[(i+1)%n][1]-slab_ring[(i+1)%n][0]*slab_ring[i][1] for i in range(n))>0
    for i in range(n):
        a=Vector(slab_ring[i]); b=Vector(slab_ring[(i+1)%n]); d=b-a; Ln=d.length
        if Ln<step: continue
        d.normalize(); inn=Vector((-d.y,d.x)) if ccw else Vector((d.y,-d.x))
        k=int(Ln//step)
        for t in range(1,k+1):
            if random.random()<0.25: continue
            p=a+d*(t*Ln/(k+1)); q=p+inn*(depth-0.15); p2=p+inn*0.9   # 0.9 m clear of the glass (corridor-less office fronts)
            v=[bm.verts.new((p2.x,p2.y,z0)),bm.verts.new((q.x,q.y,z0)),bm.verts.new((q.x,q.y,z1)),bm.verts.new((p2.x,p2.y,z1))]
            bm.faces.new(v); cnt+=1
    print('QU partitions',name,cnt); return mkobj(name,bm,part)
# ground storey (glass 136.6-142.3 on the 1.2 m inset line): lobby/lounge-like, terrazzo, 7 m deep
slab(P['G_slab'],136.68,True,'G_floor',terr); slab(P['G_slab'],142.22,False,'G_ceiling',c); band(P['G_back'],136.68,142.22,'G_back_wall',wall)
# middle ribbon storey (glass 143.2-145.7, 0.16 m behind the outer line)
slab(P['R_slab'],143.10,True,'R_floor',carp); slab(P['R_slab'],145.95,False,'R_ceiling',c); band(P['R_back'],143.10,145.95,'R_back_wall',wall)
partitions(P['R_slab'],6.2,143.10,145.95,'R_partitions',7.5); blinds(P['R_blind'],145.70,2.3,'R_blinds',1.5)
# top storey (punched windows 147.9-149.8)
slab(P['T_slab'],147.80,True,'T_floor',carp); slab(P['T_slab'],150.05,False,'T_ceiling',c); band(P['T_back'],147.80,150.05,'T_back_wall',wall)
partitions(P['T_slab'],5.2,147.80,150.05,'T_partitions',6.0); blinds(P['T_blind'],149.80,1.7,'T_blinds',1.0)
# ---------- close-up camera on the SE ground-storey glass
# pick the longest inset edge whose outward normal points at the SE eye camera
I=json.load(open('data/qp/rich_poly.json'))['inset']; n=len(I); best=None; tgt=Vector((135,245))
for i in range(n):
    a=Vector(I[i]); b=Vector(I[(i+1)%n]); d=b-a; Ln=d.length; d.normalize(); out_=Vector((d.y,-d.x))  # inset ring CCW -> right normal is outward
    m=(a+b)/2
    if out_.dot((tgt-m).normalized())>0.6 and (best is None or Ln>best[0]): best=(Ln,a,b,out_)
Ln,a,b,out_=best; m=(a+b)/2; d=(b-a).normalized()
cd=bpy.data.cameras.new('QU_CAM_closeup_richardson_glass_interior'); cd.lens=28
cam=bpy.data.objects.new('QU_CAM_closeup_richardson_glass_interior',cd); col.objects.link(cam)
cam.location=(m.x+out_.x*5.0+d.x*2.0,m.y+out_.y*5.0+d.y*2.0,138.25)
t=Vector((m.x-d.x*0.5,m.y-d.y*0.5,138.9)); cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler()
print('QU cam',tuple(round(v,2) for v in cam.location),'edge len',round(Ln,1))
if os.environ.get('QUSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

# ws87: (1) WS77 lot median island grass -> dark bark mulch (Joe catwalk_01/03/04 photos 2026-11-12: curbed mulch median with trees, not lawn)
# (2) WS87 Cole terrace white statues (Joe 9:19 AM, catwalk_07/08): 5 low-poly matte white life-size figures under the arched wall, terrace side.
import bpy,bmesh,math,os,random
from mathutils import Vector,Matrix
isl=bpy.data.objects['WS77_lot_median_island_ortho2020_UNVERIFIED_edges']
mul=bpy.data.materials['WS3_Mulch_bark_dark_brown']
for i,m in enumerate(isl.data.materials):
    if m and 'lawn' in m.name.lower(): isl.data.materials[i]=mul; print('A87 island slot',i,'->',mul.name)
isl.name='WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020'
# statues
for o in [o for o in bpy.data.objects if o.name.startswith('WS87_Cole_terrace_statue')]: bpy.data.objects.remove(o)
mat=bpy.data.materials.get('WS87_statue_matte_white') or bpy.data.materials.new('WS87_statue_matte_white')
mat.use_nodes=True; b=mat.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(0.80,0.80,0.78,1); b.inputs['Roughness'].default_value=0.85
def figure(name,h,pose):
    bm=bmesh.new(); s=h/1.75
    def cyl(r1,r2,d,loc,rot=None,seg=10):
        g=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r1*s,radius2=r2*s,depth=d*s)
        M=Matrix.Translation(Vector(loc)*s)@(rot or Matrix.Identity(4))
        bmesh.ops.transform(bm,matrix=M,verts=g['verts'])
    sp=pose
    cyl(0.065,0.08,0.85,(-0.1,0,0.43),Matrix.Rotation(0.04*sp,4,'Y'))   # legs
    cyl(0.065,0.08,0.85,(0.1,0,0.43),Matrix.Rotation(-0.04*sp,4,'Y'))
    cyl(0.17,0.21,0.62,(0,0,1.15))   # torso
    cyl(0.12,0.17,0.12,(0,0,0.84))   # hips
    cyl(0.045,0.05,0.62,(-0.25,0.02*sp,1.12),Matrix.Rotation(0.12,4,'Y')@Matrix.Rotation(0.15*sp,4,'X'))
    cyl(0.045,0.05,0.62,(0.25,0,1.12),Matrix.Rotation(-0.12,4,'Y'))
    cyl(0.05,0.05,0.08,(0,0,1.50))   # neck
    g=bmesh.ops.create_uvsphere(bm,u_segments=12,v_segments=8,radius=0.11*s)
    bmesh.ops.transform(bm,matrix=Matrix.Translation((0,0,1.63*s))@Matrix.Diagonal((0.9,1,1.12,1)),verts=g['verts'])
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(mat); return me
coll=isl.users_collection[0]
A=Vector((-182.8,-73.9)); B=Vector((-173.1,-95.2)); d=(B-A).normalized(); nrm=Vector((-d.y,d.x))
if nrm.x>0: nrm=-nrm   # terrace / camera side = west
random.seed(87); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
spots=[(0.16,1.2),(0.22,2.1),(0.30,1.0),(0.37,1.8),(0.45,1.3)]
for k,(t,off) in enumerate(spots):
    p=A+(B-A)*t+nrm*off
    ok,loc,n,i,o,_=sc.ray_cast(dg,Vector((p.x,p.y,131.6)),Vector((0,0,-1)))
    z=loc.z if ok else 129.8
    ob=bpy.data.objects.new(f'WS87_Cole_terrace_statue_{k+1}_white_JOE20261112_lowpoly_UNVERIFIED_pose',figure(f'WS87_statue_{k}',random.uniform(1.68,1.82),random.choice((-1,1))))
    ob.location=(p.x,p.y,z-0.01); ob.rotation_euler=(0,0,math.atan2(nrm.y,nrm.x)-math.pi/2+random.uniform(-0.9,0.9))
    coll.objects.link(ob); print('A87 statue',k+1,round(p.x,2),round(p.y,2),round(z,2),o.name[:30] if ok else 'nohit')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A87 saved')

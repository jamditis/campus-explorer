# nv (Oct 30 2026 ~9:40 PM ET, MAIN): CCOM 1F fill under/around the 2F back hallway (terrain/grass showed through at 1F level
# x -2.1..10, y 14..22 beside the N classroom) -> blocked-out 1F floor pieces + a 1F back service corridor shell under the 2F back
# hallway; big blocked-out floors get a subtle saw-cut joint grid + per-bay tone (material swap, revertable); NV cameras incl. a
# near-plan cutaway aerial that reads into the N classroom. ALL UNVERIFIED (no photo of the 1F under the back hallway).
import bpy, os, json, mathutils, bmesh
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NV_CCOM_1F_back_fill_floor_joints_20261030nv'; sc=bpy.context.scene
MATN='NV_blocked_out_floor_joints_UNVERIFIED'; OLD='NQ_blocked_out_interior_floor_UNVERIFIED'
def revert():
    st=json.loads(sc.get('nv_state','{}'))
    for mn,mats in st.get('meshmats',{}).items():
        me=bpy.data.meshes.get(mn)
        if me:
            for i,m in enumerate(mats):
                if i<len(me.materials): me.materials[i]=bpy.data.materials.get(m) if m else None
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    m=bpy.data.materials.get(MATN)
    if m and m.users==0: bpy.data.materials.remove(m)
    o_=bpy.data.materials.get(OLD)
    if o_ and 'old_fake' in st: o_.use_fake_user=st['old_fake']
    for k in ('nv_state','nv_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'meshmats':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nv'; o['msu_verified']='UNVERIFIED'
# --- material: blocked-out grey + 2.44 m saw-cut joint grid (3 cm, darker) + per-bay tone (+-4%), world space
old=bpy.data.materials[OLD]; state['old_fake']=old.use_fake_user; old.use_fake_user=True  # keep it in the file while unused (REVERT needs it)
ob=old.node_tree.nodes.get('Principled BSDF')
base=tuple(ob.inputs['Base Color'].default_value) if ob else (0.42,0.41,0.40,1)
m=bpy.data.materials.new(MATN); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
b=N['Principled BSDF']; b.inputs['Roughness'].default_value=0.62
geo=N.new('ShaderNodeNewGeometry'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'],sep.inputs[0])
S=float(os.environ.get('JS','2.44')); JW=float(os.environ.get('JW','0.03'))
def axis(o):
    d=N.new('ShaderNodeMath'); d.operation='DIVIDE'; d.inputs[1].default_value=S; L.new(sep.outputs[o],d.inputs[0])
    f=N.new('ShaderNodeMath'); f.operation='FRACT'; L.new(d.outputs[0],f.inputs[0])
    p=N.new('ShaderNodeMath'); p.operation='PINGPONG'; p.inputs[1].default_value=0.5; L.new(f.outputs[0],p.inputs[0])  # distance to nearest line (in cells)
    lt=N.new('ShaderNodeMath'); lt.operation='LESS_THAN'; lt.inputs[1].default_value=JW/2/S; L.new(p.outputs[0],lt.inputs[0])
    fl=N.new('ShaderNodeMath'); fl.operation='FLOOR'; L.new(d.outputs[0],fl.inputs[0])
    return lt,fl
jx,fx=axis('X'); jy,fy=axis('Y')
jm=N.new('ShaderNodeMath'); jm.operation='MAXIMUM'; L.new(jx.outputs[0],jm.inputs[0]); L.new(jy.outputs[0],jm.inputs[1])
cv=N.new('ShaderNodeCombineXYZ'); L.new(fx.outputs[0],cv.inputs[0]); L.new(fy.outputs[0],cv.inputs[1])
wn=N.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='3D'; L.new(cv.outputs[0],wn.inputs['Vector'])
mr=N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value=0.93; mr.inputs['To Max'].default_value=1.05; L.new(wn.outputs['Value'],mr.inputs['Value'])
ns=N.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value=0.9; ns.inputs['Detail'].default_value=3
mr2=N.new('ShaderNodeMapRange'); mr2.inputs['To Min'].default_value=0.96; mr2.inputs['To Max'].default_value=1.04; L.new(ns.outputs['Fac'],mr2.inputs['Value'])
L.new(geo.outputs['Position'],ns.inputs['Vector'])
mul=N.new('ShaderNodeMath'); mul.operation='MULTIPLY'; L.new(mr.outputs[0],mul.inputs[0]); L.new(mr2.outputs[0],mul.inputs[1])
jf=N.new('ShaderNodeMapRange'); jf.inputs['To Min'].default_value=1.0; jf.inputs['To Max'].default_value=0.68; L.new(jm.outputs[0],jf.inputs['Value'])
tot=N.new('ShaderNodeMath'); tot.operation='MULTIPLY'; L.new(mul.outputs[0],tot.inputs[0]); L.new(jf.outputs[0],tot.inputs[1])
rgb=N.new('ShaderNodeRGB'); rgb.outputs[0].default_value=base
mx=N.new('ShaderNodeVectorMath'); mx.operation='SCALE'; L.new(rgb.outputs[0],mx.inputs[0]); L.new(tot.outputs[0],mx.inputs['Scale'])
L.new(mx.outputs[0],b.inputs['Base Color'])
m.use_fake_user=False
# swap OLD -> NV on every mesh using it
for me in bpy.data.meshes:
    if any(mm and mm.name==OLD for mm in me.materials):
        state['meshmats'][me.name]=[mm.name if mm else None for mm in me.materials]
        for i,mm in enumerate(me.materials):
            if mm and mm.name==OLD: me.materials[i]=m
print('NV swapped meshes',len(state['meshmats']))
# --- 1F fill floor pieces (top 137.74 just above the LiDAR terrain 137.5-137.7 that showed through; NK carpet 137.68-137.71 untouched footprint)
def box(nm,x0,x1,y0,y1,z0,z1,mat,inward=False,layer='floor'):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
    if inward: bmesh.ops.reverse_faces(bm,faces=bm.faces)
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(nm,me); col.objects.link(o); tag(o,layer); return o
ZT=float(os.environ.get('ZT','137.74'))
box('NV 1F fill floor W of N classroom (UNVERIFIED)',-2.12,-0.6,14.07,17.9,136.9,ZT,m)
box('NV 1F fill floor N of atrium N wall x -9..-2 (UNVERIFIED)',-9.0,-2.12,16.68,19.0,136.9,ZT,m)
box('NV 1F fill floor N strip behind N classroom (UNVERIFIED)',-2.2,8.5,17.9,22.0,136.9,ZT,m)
box('NV 1F fill floor E of N classroom under 2F back hallway (UNVERIFIED)',6.6,8.5,14.07,17.9,136.9,ZT,m)
box('NV 1F fill floor E of 2F back hallway x 8.5..11.2 (UNVERIFIED)',8.5,11.2,13.3,19.6,136.9,ZT,m)
wall=bpy.data.materials.get('NK_room_wall_warm_white_UNVERIFIED')
box('NV 1F back service corridor room shell under 2F back hallway (inward, UNVERIFIED)',6.65,8.45,14.12,17.92,ZT,141.4,wall,inward=True,layer='room')
box('NV 1F back room shell under the 2F back hallway end (inward, UNVERIFIED)',5.55,8.45,17.95,21.95,ZT,141.4,wall,inward=True,layer='room')  # carries the 2F hallway end (no 1.1 m cantilever)
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('NV_CAM_aerial_cutaway_plan_N_classroom_back_hallway',f('ALOC','4,8,174'),f('ATGT','3,14,138'),float(os.environ.get('ALENS','30')))
camcopy('NV_CAM_eye_atrium_looking_west_to_doors','NU_CAM_eye_atrium_looking_west_to_doors')
camcopy('NV_CAM_eye_1F_open_floor_cafe_looking_east','NU_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NV_CAM_closeup_cutaway_back_corridor_floor_joints',f('CLLOC','-1.5,24.5,146'),f('CLTGT','5.5,16.5,138.4'),float(os.environ.get('CLLENS','28')))
sc['nv_state']=json.dumps(state)
sc['nv_note']='nv: 1F fill floors + back service corridor shell under the 2F back hallway; blocked-out floor joint grid material; NV cameras; UNVERIFIED'
print('NV objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

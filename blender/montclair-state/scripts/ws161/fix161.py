# ws161: UNIFY #65 Panzer gym S/W façades — clerestory ribbon above the NW annex + N-gym W wall, pool-block high windows,
#        doors where OSM footways end (W a-4.9; E corner a-14.4), S gable egress pair + mid-block service pair (UNVERIFIED),
#        louvres seen in cch_3, off-white wall + light eave trim (cch_3), gutters/downspouts on the S-block eaves and N-gym W eave.
# Base: ws160b if present else ws160a (run with either file loaded; idempotent: removes an existing WS161 collection first).
import bpy, bmesh, math, json, os
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
th=math.radians(76.8); A=Vector((math.cos(th),math.sin(th),0)); B=Vector((math.cos(th-math.pi/2),math.sin(th-math.pi/2),0)); O=Vector((-238.1,-180.2,0))
def P(a,b,z): return O+A*a+B*b+Vector((0,0,z))
F=json.load(open(M+'prep/ws160_gymroof/fit160.json')); NG,SG=F['N'],F['S']; ZX=F['annex']
def zg(G,b): return G['zr']-G['s']*abs(b-G['br'])
old=bpy.data.collections.get('WS161_Panzer_gym_facades_S_W')
if old:
    for o in list(old.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(old)
col=bpy.data.collections.new('WS161_Panzer_gym_facades_S_W'); bpy.context.scene.collection.children.link(col)
def mat(n,rgb,rough=0.6,metal=0.0):
    m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal; return m
# --- colour decisions from cch_3 (night photo): gym walls behind the lobby read off-white, eave edge a pale band, roof light grey ---
GYW=bpy.data.materials.get('WS158_gym_wall_lightgrey_UNVERIFIED')
if GYW: GYW.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.78,0.77,0.74,1); GYW.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.8
FAS=bpy.data.materials.get('WS160_gym_fascia_dark_bronze_UNVERIFIED')
if FAS:
    bs=FAS.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(0.70,0.71,0.70,1); bs.inputs['Metallic'].default_value=0.3
GLS=mat('WS161_clerestory_glass_dark',(0.035,0.045,0.055),0.08,0.0)
FRM=mat('WS161_window_frame_aluminium_clear',(0.60,0.61,0.60),0.4,0.6)
DOR=mat('WS161_hollow_metal_door_grey_UNVERIFIED',(0.30,0.31,0.32),0.45,0.3)
LOU=mat('WS161_louvre_dark_grey',(0.12,0.12,0.12),0.5,0.4)
CON=bpy.data.materials.get('WS159_bed_edge_concrete_curb') or mat('WS161_concrete_pad',(0.55,0.54,0.51),0.85)
GUT=mat('WS161_gutter_downspout_light_grey',(0.68,0.69,0.68),0.45,0.4)
V=[];FC=[];MI=[]; ML=[GLS,FRM,DOR,LOU,CON,GUT]
def box(a0,a1,b0,b1,z0,z1,k):
    o=len(V); V.extend([P(a0,b0,z0),P(a1,b0,z0),P(a1,b1,z0),P(a0,b1,z0),P(a0,b0,z1),P(a1,b0,z1),P(a1,b1,z1),P(a0,b1,z1)])
    for q in ([0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]): FC.append([i+o for i in q]); MI.append(k)
# face helper: on a wall plane at b=bw (axis 'b', out = sign of outward normal along B) or a=aw (axis 'a'); u = along-wall coord
def onwall(axis,w,out,u0,u1,z0,z1,d0,d1,k):
    lo,hi=(w+out*d0,w+out*d1) if out>0 else (w+out*d1,w+out*d0)
    if axis=='b': box(u0,u1,lo,hi,z0,z1,k)
    else: box(lo,hi,u0,u1,z0,z1,k)
def window(axis,w,out,u0,u1,z0,z1,fw=0.07):
    onwall(axis,w,out,u0,u1,z0,z1,0.0,0.04,0)                  # glass (dark)
    for (a,b_,c,d) in ((u0,u1,z0,z0+fw),(u0,u1,z1-fw,z1),(u0,u0+fw,z0,z1),(u1-fw,u1,z0,z1)): onwall(axis,w,out,a,b_,c,d,0.0,0.07,1)
    onwall(axis,w,out,u0-0.05,u1+0.05,z0-0.09,z0,0.0,0.12,1)    # sill flashing
def ribbon(axis,w,out,u0,u1,z0,z1,unit=2.4):
    n=max(1,int(round((u1-u0)/unit))); du=(u1-u0)/n
    onwall(axis,w,out,u0,u1,z0,z1,0.0,0.04,0)
    for i in range(n+1): onwall(axis,w,out,u0+i*du-0.05,u0+i*du+0.05,z0,z1,0.0,0.08,1)
    onwall(axis,w,out,u0,u1,z1-0.08,z1,0.0,0.08,1); onwall(axis,w,out,u0-0.05,u1+0.05,z0-0.09,z0,0.0,0.12,1)
def door(axis,w,out,uc,width,zg_,h=2.2,pair=True):
    u0,u1=uc-width/2,uc+width/2
    onwall(axis,w,out,u0-0.08,u1+0.08,zg_,zg_+h+0.08,0.0,0.05,1)  # frame
    onwall(axis,w,out,u0,u1,zg_,zg_+h,0.0,0.07,2)                  # leaves
    if pair: onwall(axis,w,out,uc-0.012,uc+0.012,zg_,zg_+h,0.0,0.08,1)
    onwall(axis,w,out,u0+0.15,u1-0.15,zg_+1.0,zg_+1.04,0.07,0.10,1)  # push bar
    onwall(axis,w,out,u0-0.5,u1+0.5,zg_-0.15,zg_+0.05,0.0,1.6,4)   # concrete landing pad
# 1) N gym W clerestory ribbon (above the NW annex roof and on the exposed W wall), b = -47.25 facing W (-B)
zE=zg(NG,-47.25); z0=ZX+0.45; z1=zE-0.5
ribbon('b',-47.25,-1,-13.6,21.0,z0,z1)
# 2) S block (natatorium, UNVERIFIED) high windows in the frame bays, W wall b=-40.7 (out -B) and E wall b=-16.55 (out +B)
for bw,out in ((-40.7,-1),(-16.55,1)):
    ze=zg(SG,bw); zt=ze-0.55; zb=zt-1.5
    for k in range(5):
        ac=-64.1+k*6.1; window('b',bw,out,ac-0.9,ac+0.9,zb,zt)
# 3) doors
door('b',-47.25,-1,-6.0,1.8,118.45)                  # W door where OSM footway 312847987 meets the wall
door('a',-14.4,-1,-10.6,1.8,118.73)                  # E-corner door at the end of the lower walk OSM 312847982 (faces S)
door('a',-67.85,-1,-28.6,1.8,118.66)                 # S gable egress pair (UNVERIFIED)
door('b',-45.3,-1,-27.0,1.8,118.45)                  # mid-block service pair facing Lot 3 (UNVERIFIED; LiDAR: no dock, lot at grade)
# 4) louvres (cch_3: dark rectangles high on the gym walls N and S of the lobby, facing College Ave)
onwall('b',-9.0,1,27.6,29.4,126.2,127.4,0.0,0.06,3)
onwall('b',-12.3,1,-21.0,-19.2,125.9,127.1,0.0,0.06,3)
# 5) gutters + downspouts: S block eaves (b0-0.35, b1+0.35) and N gym W eave
def gutter(a0,a1,be,ze,out,downs,zground):
    lo,hi=(be,be+out*0.16) if out>0 else (be+out*0.16,be)
    box(a0,a1,lo,hi,ze-0.32,ze-0.16,5)
    for ad in downs:
        bc=be+out*0.08; box(ad-0.05,ad+0.05,bc-0.05+out*0.0,bc+0.05,zground,ze-0.3,5)
gutter(-68.1,-37.2,-41.05,zg(SG,-41.05),-1,(-67.5,-52.6,-38.0),118.44)
gutter(-68.1,-37.6,-16.20,zg(SG,-16.20),1,(-67.5,-52.6),118.75)
gutter(-14.5,33.75,-47.60,zg(NG,-47.60),-1,(-13.9,),118.42)
# 6) review fix (ws160b SE oblique): black slot where the flat link block meets the S gable on the College Ave side — outline edge
#    a -37.7 (b -16.5..-12.3) sat 0.3 m outside the a -37.4 section snap, so its wall took the low S-gable top. Plug wall at a -37.45.
ZM=F['mid']; GV=[];GF=[]
for (b0,b1) in ((-16.75,-12.1),):
    o=len(GV); GV.extend([P(-37.45,b0,117.0),P(-37.45,b1,117.0),P(-37.45,b1,ZM+0.28),P(-37.45,b0,ZM+0.28),
                          P(-37.75,b0,117.0),P(-37.75,b1,117.0),P(-37.75,b1,ZM+0.28),P(-37.75,b0,ZM+0.28)])
    for q in ([0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]): GF.append([i+o for i in q])
gm=bpy.data.meshes.new('WS161_Panzer_link_block_S_corner_plug_wall'); gm.from_pydata([tuple(v) for v in GV],[],GF)
if GYW: gm.materials.append(GYW)
col.objects.link(bpy.data.objects.new(gm.name,gm))
me=bpy.data.meshes.new('WS161_Panzer_gym_SW_facade_openings_cch_OSM_LiDAR_UNVERIFIED'); me.from_pydata([tuple(v) for v in V],[],FC)
for m in ML: me.materials.append(m)
for p,k in zip(me.polygons,MI): p.material_index=k
bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new(me.name,me); col.objects.link(ob)
print('FIX161 faces',len(FC))
src=bpy.data.filepath; print('FIX161 base',os.path.basename(src))
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws161a.blend',compress=True)
print('FIX161 SAVED')

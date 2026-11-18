# nz (Oct 31 2026 ~1:40 AM ET, MAIN, CCOM N classroom): generic ceiling projector on a drop pole, surface-mounted pull-down
# projection screen case above the whiteboard, stroke-like whiteboard ghosting (new material on the ny overlay; ny material
# kept and restored on REVERT), duplex outlets / light switch / AV wall plate, NZ cameras. ALL UNVERIFIED (no photo of the room).
import bpy, os, json, sys, mathutils
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sys.path.insert(0,os.path.abspath('scripts/nz')); import importlib, nz_geo; importlib.reload(nz_geo); G=nz_geo
CN='NZ_CCOM_N_classroom_projector_screen_plates_20261031nz'; sc=bpy.context.scene
GHO='NY N classroom whiteboard ghosting overlay (UNVERIFIED)'; GMAT='NZ_whiteboard_ghosting_strokes_UNVERIFIED'
def revert():
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    if 'nz_state' in sc:
        st=json.loads(sc['nz_state']); g=bpy.data.objects.get(GHO)
        if g and st.get('ghost_mat'):
            m0=bpy.data.materials[st['ghost_mat']]; g.material_slots[0].material=m0
            if st.get('ghost_fake'): m0.use_fake_user=False
    for m in list(bpy.data.materials):
        if m.name.startswith('NZ_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('nz_state','nz_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nz'; o['msu_verified']='UNVERIFIED'
MT=G.mats('NZ')
def put(prefix,parts,layer='furniture',bevel=None):
    n=0
    for nm,me,mk in parts:
        o=bpy.data.objects.new('NZ N classroom %s %s (UNVERIFIED)'%(prefix,nm),me); col.objects.link(o); tag(o,layer); me.materials.append(MT[mk])
        if bevel and nm in bevel:
            b=o.modifiers.new('NZ bevel','BEVEL'); b.width=bevel[nm]; b.segments=3; b.limit_method='ANGLE'
        n+=1
    return n
# room: x -0.6..6.6, y 14.08..17.9, floor 137.71 (carpet top), ceiling grid underside 140.89; board x 0.6..5.4 on y 17.86..17.88
ZC=140.888
n=put('ceiling projector',G.projector((3.0,16.25,ZC)),bevel={'body':0.014})
n+=put('pull-down screen',G.screen_case(1.75,4.25,17.62,ZC),bevel={'case':0.012})
ZO=137.71+0.457   # outlets 18 in above the floor
for kind,c,nn,lab in (('duplex',(-0.6,15.3,ZO),(1,0),'W wall outlet 1'),('duplex',(-0.6,16.6,ZO),(1,0),'W wall outlet 2'),
                      ('duplex',(6.6,15.3,ZO),(-1,0),'E wall outlet 1'),('duplex',(6.6,16.6,ZO),(-1,0),'E wall outlet 2'),
                      ('duplex',(0.25,17.9,ZO),(0,-1),'N wall outlet'),('av',(5.75,17.9,ZO),(0,-1),'N wall AV (HDMI) plate'),
                      ('duplex',(3.0,17.9,140.62),(0,-1),'N wall high outlet (screen)'),
                      ('switch',(2.12,14.08,137.71+1.22),(0,1),'light switch by door'),('switch',(6.0,14.08,137.71+1.22),(0,1),'light switch by E door')):
    n+=put(lab,G.wall_plate(kind,c,nn))
state['parts']=n
# stroke-like ghosting: swap the ny overlay material (keep ny material via fake user so REVERT can restore it)
g=bpy.data.objects.get(GHO)
if g:
    old=g.material_slots[0].material; state['ghost_mat']=old.name
    g.material_slots[0].material=G.ghost_material(GMAT,float(os.environ.get('GHOST','0.38')))
    if old.users==0: old.use_fake_user=True; state['ghost_fake']=True
# cameras
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
camcopy('NZ_CAM_aerial_cutaway_oblique_CCOM_from_SW','NY_CAM_aerial_cutaway_oblique_CCOM_from_SW')
camcopy('NZ_CAM_eye_atrium_looking_west_to_doors','NY_CAM_eye_atrium_looking_west_to_doors')
camcopy('NZ_CAM_eye_1F_open_floor_cafe_looking_east','NY_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NZ_CAM_closeup_N_classroom_projector_screen_board',f('CLLOC','6.2,14.35,138.85'),f('CLTGT','2.2,17.4,139.75'),float(os.environ.get('CLLENS','20')))
sc['nz_state']=json.dumps(state)
sc['nz_note']='nz: N classroom ceiling projector + pull-down screen case, outlets/switches/AV plate, stroke-like board ghosting; NZ cameras; UNVERIFIED'
print('NZ objects',len(col.objects),'total',len(bpy.data.objects),state)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

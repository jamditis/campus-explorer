# nt (Oct 30 2026 ~7:35 PM ET, MAIN): CCOM 1F open-floor polish from ns 'Next' — ALL UNVERIFIED:
# (a) cafe chairs: NR shell chairs (flat seat pan + flat back panel, read boxy) -> one-piece moulded shell (dished seat, wrapped back, 7 mm shell)
#     on splayed tube legs (scripts/nt/nt_furn_lib.py); NR chairs hidden (stored, revertable); NG orange/white shell colours kept per chair.
# (b) NT cameras (new cutaway aerial framed on the 1F open floor; eye + close-up copies). Cutaway hides are render-time only (scripts/nt/nt_render.py).
import bpy, bmesh, os, json, mathutils, math, sys
sys.path.insert(0,os.path.abspath('scripts/nt'))
import importlib, nt_furn_lib as FL; importlib.reload(FL)
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NT_CCOM_1F_open_floor_shell_chairs_20261030nt'
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('nt_state','{}'))
    for n,mn in st.get('matslot',{}).items():
        o=bpy.data.objects.get(n); m=bpy.data.materials.get(mn)
        if o and m: o.material_slots[0].material=m
    for n,(bl,sz) in st.get('spots',{}).items():
        o=bpy.data.objects.get(n)
        if o and o.type=='LIGHT': o.data.spot_blend=bl; o.data.shadow_soft_size=sz
    for n,(hr,hv) in st.get('hidden',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                for coll in (bpy.data.meshes,bpy.data.cameras):
                    if d.name in coll and coll[d.name]==d: coll.remove(d); break
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.name.startswith('NT_') and me.users==0: bpy.data.meshes.remove(me)
    for m in list(bpy.data.materials):
        if m.name.startswith('NT_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('nt_state','nt_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'hidden':{},'matslot':{},'spots':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nt'; o['msu_verified']='UNVERIFIED'
def hide(o):
    if o.name not in state['hidden']: state['hidden'][o.name]=(o.hide_render,o.hide_viewport)
    o.hide_render=True; o.hide_viewport=True
charcoal=bpy.data.materials['NR_powder_coat_charcoal_UNVERIFIED']; glide=bpy.data.materials['NR_black_nylon_UNVERIFIED']
seatm=bpy.data.objects['NG cafe chair 0_0 seat'].active_material
bm=bmesh.new(); FL.shell_chair(bm); me=bpy.data.meshes.new('NT_cafe_moulded_shell_chair_UNVERIFIED'); bm.to_mesh(me); bm.free()
for m in (seatm,charcoal,glide): me.materials.append(m)
n=0
for t in range(4):
    for k in range(2):
        old=bpy.data.objects.get('NR cafe shell chair %d_%d (UNVERIFIED)'%(t,k))
        if not old: continue
        o=bpy.data.objects.new('NT cafe moulded shell chair %d_%d (UNVERIFIED)'%(t,k),me); o.matrix_world=old.matrix_world.copy()
        col.objects.link(o); tag(o,'furniture')
        sl=o.material_slots[0]; sl.link='OBJECT'; sl.material=old.material_slots[0].material
        wn=o.modifiers.new('NT_wn','WEIGHTED_NORMAL'); wn.keep_sharp=True
        hide(old); n+=1
# (c) the NG 1F south rooms floor blockout was wall-white and read as a white roof slab in the cutaway aerial -> same grey as the NQ blocked-out floor (UNVERIFIED either way)
fo=bpy.data.objects.get('NG 1F south rooms floor blockout UNVERIFIED'); gm=bpy.data.materials.get('NQ_blocked_out_interior_floor_UNVERIFIED')
if fo and gm and fo.material_slots[0].material!=gm:
    state['matslot'][fo.name]=fo.material_slots[0].material.name; fo.material_slots[0].material=gm
# (d) ceiling-spot glare: softer spot edges + larger emitter radius on the CCOM interior spots (hot streaks on walls/pilasters), energy unchanged
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.data.type=='SPOT':
        p_=o.matrix_world.translation
        if -21.5<p_.x<13 and 2<p_.y<23 and 137<p_.z<147.5 and o.name not in state['spots']:
            state['spots'][o.name]=(o.data.spot_blend,o.data.shadow_soft_size)
            o.data.spot_blend=max(o.data.spot_blend,0.75); o.data.shadow_soft_size=max(o.data.shadow_soft_size,0.09)
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
cam('NT_CAM_aerial_cutaway_1F_open_floor_oblique',tuple(float(x) for x in os.environ.get('AERLOC','4,-10,168').split(',')),tuple(float(x) for x in os.environ.get('AERTGT','-1,11,138').split(',')),float(os.environ.get('AERLENS','30')))
camcopy('NT_CAM_eye_1F_open_floor_cafe_looking_east','NS_CAM_eye_1F_open_floor_cafe_looking_east')
camcopy('NT_CAM_eye_atrium_looking_west_to_doors','NS_CAM_eye_atrium_looking_west_to_doors')
cam('NT_CAM_closeup_cafe_moulded_shell_chairs',(5.75,8.15,138.75),(4.5,10.5,138.15),28)
if 'NP_CAM_closeup_hallway_N_wall_strobe_plaque_sprinkler' in bpy.data.objects:
    camcopy('NT_CAM_closeup_strobe_lens_glint','NP_CAM_closeup_hallway_N_wall_strobe_plaque_sprinkler'); bpy.data.objects['NT_CAM_closeup_strobe_lens_glint'].data.lens*=1.8
sc['nt_state']=json.dumps(state)
sc['nt_note']='nt: cafe chairs -> moulded shell chairs; cutaway aerial opens the 2F over the 1F open floor (render-time only); ALL UNVERIFIED'
print('NT chairs',n,'spots',len(state['spots']),'objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

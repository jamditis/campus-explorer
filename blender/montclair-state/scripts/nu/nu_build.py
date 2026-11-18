# nu (Oct 30 2026 ~8:45 PM ET, MAIN): CCOM atrium red-wall washers respaced over the red panel (x -16.0..-2.3) — washer 0 sat 3 m west
# of the panel (x -19) and threw a hot streak up the white wall/pilaster beside the entrance; NU cameras. Section poche caps are render-time
# only (scripts/nu/nu_render.py). ALL UNVERIFIED (no photo of the atrium lighting).
import bpy, os, json, mathutils
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NU_CCOM_atrium_washers_cutaway_cams_20261030nu'; sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('nu_state','{}'))
    for n,loc in st.get('loc',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.location=loc
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0 and d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
        bpy.data.collections.remove(c)
    for k in ('nu_state','nu_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'loc':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nu'; o['msu_verified']='UNVERIFIED'
X0,X1=-16.0,-2.3
for i in range(4):
    nx=round(X0+(X1-X0)*(i+0.5)/4,3); base='NO atrium red-wall washer %d'%i
    for n in (base,base+' can trim',base+' can lens'):
        o=bpy.data.objects.get(n)
        if not o: continue
        state['loc'][n]=tuple(o.location)
        dx=nx-(-19.0,-15.6,-10.2,-5.6)[i]; o.location.x+=dx
    print('washer',i,'->',nx)
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
camcopy('NU_CAM_aerial_cutaway_1F_open_floor_oblique','NT_CAM_aerial_cutaway_1F_open_floor_oblique')
camcopy('NU_CAM_eye_atrium_looking_west_to_doors','NT_CAM_eye_atrium_looking_west_to_doors')
camcopy('NU_CAM_eye_1F_open_floor_cafe_looking_east','NT_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NU_CAM_closeup_cutaway_section_poche_rooms',tuple(float(x) for x in os.environ.get('CLLOC','8.5,-3,151').split(',')),tuple(float(x) for x in os.environ.get('CLTGT','3.5,9,138.5').split(',')),float(os.environ.get('CLLENS','30')))
sc['nu_state']=json.dumps(state)
sc['nu_note']='nu: atrium red-wall washers respaced over the red panel; NU cameras; cutaway poche render-time only; UNVERIFIED'
print('NU objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

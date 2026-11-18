# oa (Oct 31 2026 ~2:40 AM ET, MAIN, CCOM 2F main hallway / student area, Joe's first-priority 2F main areas): the 7 x 10.7 m 2F
# hallway between the atrium bridge and the east balcony was empty. Adds a furnished student area: lounge cluster on a loop-pile rug
# (4 club chairs + low table), sofa + chair + table by the S wall under a wall-mounted signage display, a wall study counter with
# power/USB modules and 6 bar stools along the N wall, a cork tack board with pinned flyers. OA cameras. ALL UNVERIFIED (no photo of
# the 2F hallway furniture). SAVE=1 saves, REVERT=1 removes everything oa added and saves.
import bpy, os, json, sys, math, mathutils
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sys.path.insert(0,os.path.abspath('scripts/oa')); import importlib, oa_geo; importlib.reload(oa_geo); G=oa_geo
CN='OA_CCOM_2F_student_area_lounge_counter_board_20261031oa'; sc=bpy.context.scene
assert len(CN)<=63
def revert():
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.name.startswith('OA_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('oa_state','oa_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='oa'; o['msu_verified']='UNVERIFIED'
MT=G.mats('OA'); F=141.85; RUGT=0.008; N=[0]
def put(label,parts,loc=(0,0,0),rot=0.0,remap=None,bevel=None,layer='furniture'):
    for nm,me,mk in parts:
        mk=(remap or {}).get(mk,mk)
        nmo='OA 2F %s %s (UNVERIFIED)'%(label,nm); assert len(nmo)<=63,nmo
        o=bpy.data.objects.new(nmo,me); o.location=loc; o.rotation_euler=(0,0,rot); col.objects.link(o); tag(o,layer); me.materials.append(MT[mk])
        if bevel and nm in bevel:
            b=o.modifiers.new('OA bevel','BEVEL'); b.width=bevel[nm]; b.segments=3; b.limit_method='ANGLE'
        N[0]+=1
CB={'base':0.035,'arms':0.04,'back':0.04,'seat cushion':0.03}
RED={'fab':'fabR','fab2':'fabR2'}
# lounge cluster A on the rug
put('rug A',G.rug(0.3,3.3,7.75,10.85,F),layer='floor')
zr=F+RUGT
put('chair A1',G.lounge_chair(),(1.25,8.2,zr),0.0,RED,CB); put('chair A2',G.lounge_chair(),(2.35,8.2,zr),0.0,RED,CB)
put('chair A3',G.lounge_chair(),(1.25,10.4,zr),math.pi,None,CB); put('chair A4',G.lounge_chair(),(2.35,10.4,zr),math.pi,None,CB)
put('table A',G.low_table(1.0,0.5,0.40),(1.8,9.3,zr),0.0,None,{'top':0.004})
# sofa cluster B by the S wall under the display
put('sofa B',G.sofa(1.6),(5.6,7.56,F),0.0,None,CB)
put('table B',G.low_table(1.1,0.5,0.40),(5.6,8.5,F),0.0,None,{'top':0.004})
put('chair B',G.lounge_chair(),(7.5,8.6,F),math.pi/2,RED,CB)
put('display',G.display(5.6,7.07,142.95,ny=1),layer='av')
# tack board on the S wall by the atrium
put('tack board',G.tackboard(-1.7,0.3,7.07,142.75,143.65,ny=1),layer='wall')
# wall study counter + power modules + stools on the N wall
put('counter',G.counter(-1.4,4.9,13.45,13.93,F+1.07,(-1.3,0.8,2.75,4.8)),bevel={'top':0.003})
put('counter',G.power_modules((-0.6,1.6,3.8),13.82,F+1.07))
for i,x in enumerate((-0.9,0.15,1.2,2.25,3.3,4.35)):
    put('stool %d'%(i+1),G.bar_stool(0.76),(x,13.12,F),0.3*i,None,{'seat':0.008})
# small lived-in details (UNVERIFIED): 2 open laptops on the counter, coffee cups on table A, a backpack by stool 3
put('laptop 1',G.laptop(None),(0.15,13.62,F+1.07),math.pi); put('laptop 2',G.laptop(None),(3.3,13.64,F+1.07),math.pi+0.12)
put('cup 1',G.cup(),(1.55,9.2,zr+0.40)); put('cup 2',G.cup(),(2.1,9.4,zr+0.40))
put('cup 3',G.cup(),(5.9,8.45,F+0.40))
put('backpack',G.backpack(),(1.72,12.75,F),0.35)
# 3 framed prints above the counter on the N wall + flush floor power box by lounge A (UNVERIFIED)
for i,xc in enumerate((0.0,1.75,3.5)):
    put('print %d'%(i+1),G.poster_frame(xc,13.93,143.12,0.62,0.84,ny=-1),remap={'print':'p%d'%(i+1)})
put('floor box',G.floor_box((1.8,11.05),F),layer='floor')
# cameras
def cam(nm,loc,tgt,lens_):
    assert len(nm)<=63
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('OA_CAM_aerial_cutaway_2F_student_area_from_SW',f('AELOC','-0.5,1.5,158'),f('AETGT','3.2,10.6,141.9'),float(os.environ.get('AELENS','24')))
cam('OA_CAM_eye_2F_student_area_looking_east',f('E1LOC','-1.6,12.4,143.45'),f('E1TGT','8.4,8.6,142.7'),18)
cam('OA_CAM_eye_2F_balcony_looking_west',f('E2LOC','8.1,12.9,143.45'),f('E2TGT','-2.0,8.5,142.6'),18)
cam('OA_CAM_closeup_2F_lounge_tack_board_display',f('CLLOC','3.3,10.9,142.95'),f('CLTGT','0.2,7.1,142.7'),float(os.environ.get('CLLENS','24')))
sc['oa_state']=json.dumps({'parts':N[0]})
sc['oa_note']='oa: CCOM 2F hallway student area (lounge cluster + rug, sofa/display, study counter + stools, tack board); OA cameras; UNVERIFIED'
print('OA objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

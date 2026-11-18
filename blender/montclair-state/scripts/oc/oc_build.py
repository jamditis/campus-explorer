# oc (Oct 31 2026 ~4:40 AM ET, MAIN, CCOM 1F open floor EAST END, after Joe's photos refs/joe/ccom_interior_east_1f_joe_20261020_01..05):
# the photos show big dark charcoal carpet area rugs set on the terrazzo, long white rectangular tables with light-grey upholstered
# chairs, blue tub lounge chairs at the east windows and a stainless bin. The NR small cafe tables + NT shell chairs in that zone are
# HIDDEN (not deleted) and replaced. Furniture types from the photos; exact positions/sizes/counts approximated -> UNVERIFIED.
# SAVE=1 saves, REVERT=1 removes all and unhides.
import bpy, os, json, sys, math, mathutils, bmesh, random
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sys.path.insert(0,os.path.abspath('scripts/oa')); import importlib, oa_geo; importlib.reload(oa_geo); G=oa_geo; V=mathutils.Vector
CN='OC_CCOM_1F_open_floor_east_end_rugs_tables_20261031oc'; sc=bpy.context.scene; assert len(CN)<=63
def revert():
    st=json.loads(sc.get('oc_state','{}'))
    for n in st.get('hidden',[]):
        o=bpy.data.objects.get(n)
        if o: o.hide_render=False; o.hide_viewport=False
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    for mm in list(bpy.data.materials):
        if mm.name.startswith('OC_') and mm.users==0: bpy.data.materials.remove(mm)
    if 'oc_state' in sc: del sc['oc_state']
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='oc'; o['msu_verified']='UNVERIFIED (photo-based type, approx. layout)'
def link(nm,me,mat,loc=(0,0,0),rot=0.0,layer='furniture',bevel=None):
    nmo='OC 1F %s (UNVERIFIED)'%nm; assert len(nmo)<=63,nmo
    o=bpy.data.objects.new(nmo,me); o.location=loc; o.rotation_euler=(0,0,rot); col.objects.link(o); tag(o,layer)
    for mm in (mat if isinstance(mat,(list,tuple)) else [mat]): me.materials.append(mm)
    if bevel:
        b=o.modifiers.new('OC bevel','BEVEL'); b.width=bevel; b.segments=3 if bevel>=0.02 else 2; b.limit_method='ANGLE'
        if bevel>=0.02:   # upholstered parts: smooth + hardened normals (review fix: faceted chair backs in the close-up)
            b.harden_normals=True
            for p in me.polygons: p.use_smooth=True
    return o
F=137.70
# hide old cafe set in the zone
hidden=[]
for o in bpy.data.objects:
    if o.name.startswith(('NR cafe pedestal table','NT cafe moulded shell chair')) and not o.hide_render:
        o.hide_render=True; o.hide_viewport=True; hidden.append(o.name)
RUG=G.rug_material('OC_carpet_charcoal_area_rug_UNVERIFIED')
_cr=[n for n in RUG.node_tree.nodes if n.type=='VALTORGB'][0].color_ramp; _cr.elements[0].color=(0.035,0.04,0.05,1); _cr.elements[1].color=(0.11,0.115,0.13,1)   # darker, per photos
TOP=G.pm('OC_table_top_white_laminate_UNVERIFIED',(0.80,0.80,0.78),0.35)
CHROME=G.pm('OC_table_base_polished_chrome_UNVERIFIED',(0.85,0.85,0.86),0.12,metal=1.0)
GREYF=G.fabric('OC_chair_fabric_light_grey_UNVERIFIED',(0.36,0.37,0.38))
WOOD=G.pm('OC_chair_leg_ash_UNVERIFIED',(0.45,0.33,0.21),0.45)
BLUE=G.fabric('OC_tub_chair_fabric_cobalt_blue_UNVERIFIED',(0.02,0.12,0.42),0.2)
STEEL=G.pm('OC_bin_brushed_stainless_UNVERIFIED',(0.62,0.62,0.62),0.32,metal=1.0)
BLK=G.pm('OC_bin_lid_black_UNVERIFIED',(0.02,0.02,0.02),0.5)
# 1) rugs (dark charcoal, 8 mm) — hallway run and east double-height zone
for nm,(x0,x1,y0,y1) in (('rug hallway',(0.6,8.3,8.1,12.9)),('rug east zone',(8.8,11.8,7.5,12.3))):
    bm=bmesh.new(); G.box(bm,x0,x1,y0,y1,F,F+0.008); link(nm,G.mesh('OC area rug',bm),RUG,layer='floor finish',bevel=0.003)
# 2) long tables + grey upholstered chairs
def table(nm,x,y,L=1.8,W=0.8,H=0.74,rot=0.0):
    bm=bmesh.new(); G.box(bm,-L/2,L/2,-W/2,W/2,H-0.03,H); link(nm+' top',G.mesh('OC table top',bm),TOP,(x,y,F+0.008),rot,bevel=0.004)
    bm=bmesh.new()
    for sx in (-1,1):
        cx=sx*(L/2-0.3); G.cyl(bm,(cx,0),0.03,0.03,H-0.03,16)
        G.box(bm,cx-0.03,cx+0.03,-W/2+0.08,W/2-0.08,0.0,0.03)   # T foot
        G.box(bm,cx-0.025,cx+0.025,-W/2+0.12,W/2-0.12,H-0.06,H-0.03)  # top rail
    link(nm+' base',G.mesh('OC table base',bm,True),CHROME,(x,y,F+0.008),rot)
def chair(nm,x,y,rot,seed):
    r=random.Random(seed); rot+=r.uniform(-0.12,0.12); x+=r.uniform(-0.04,0.04); y+=r.uniform(-0.04,0.04)
    bm=bmesh.new(); G.box(bm,-0.24,0.24,-0.22,0.24,0.40,0.47)   # seat (front +Y)
    G.box(bm,-0.24,0.24,-0.26,-0.20,0.47,0.86)                  # back panel
    me=G.mesh('OC chair shell',bm)
    o=link(nm,me,GREYF,(x,y,F+0.008),rot,bevel=0.025)
    # slight back recline via shear: rotate back verts
    for v in me.vertices:
        if v.co.z>0.475: v.co.y-= (v.co.z-0.47)*0.18
    bm=bmesh.new()
    for sx in (-1,1):
        for sy,(ty) in ((-1,-0.24),(1,0.21)):
            q=bmesh.ops.create_cone(bm,cap_ends=True,segments=10,radius1=0.014,radius2=0.018,depth=0.40)
            for v in q['verts']:
                t=(v.co.z+0.2)/0.4; v.co=V((v.co.x+sx*(0.20+0.03*(1-t)),v.co.y+ty+sy*0.03*(1-t),v.co.z+0.2))
    link(nm+' legs',G.mesh('OC chair legs',bm,True),WOOD,(x,y,F+0.008),rot)
tables=[('table H1',2.6,10.5),('table H2',5.6,10.5),('table E1',9.95,8.9),('table E2',9.95,11.1)]
k=0
for nm,x,y in tables:
    table(nm,x,y)
    for dx in (-0.55,0.0,0.55):
        chair(nm+' chair N%+.2f'%dx,x+dx,y+0.62,math.pi,k); k+=1
        chair(nm+' chair S%+.2f'%dx,x+dx,y-0.62,0.0,k+50); k+=1
# 3) blue tub lounge chairs by the east windows (photo 02), facing west into the room
for i,(y) in enumerate((8.0,9.4,12.0)):
    parts=G.lounge_chair(0.6)
    for pn,me,mk in parts:
        mat={'fab':BLUE,'fab2':BLUE,'steel':CHROME}[mk]
        link('blue tub chair %d %s'%(i,pn),me,mat,(11.68,y,F+0.008),math.pi/2+0.1*(i-1),bevel=0.03 if mk!='steel' else None)
# 4) stainless bin (photo 02) at the SE corner of the east zone
bm=bmesh.new(); G.cyl(bm,(0,0),0.2,0.0,0.74,32); link('stainless bin body',G.mesh('OC bin body',bm,True),STEEL,(9.05,7.35,F),bevel=0.004)
bm=bmesh.new(); G.cyl(bm,(0,0),0.205,0.74,0.80,32); link('stainless bin lid',G.mesh('OC bin lid',bm,True),BLK,(9.05,7.35,F),bevel=0.004)
def cam(nm,loc,tgt,lens_):
    assert len(nm)<=63
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(V(tgt)-V(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('OC_CAM_aerial_cutaway_1F_east_end_from_W',f('AELOC','-3.5,9.6,155'),f('AETGT','7.6,10.2,137.8'),24)
cam('OC_CAM_eye_1F_open_floor_looking_east',f('E1LOC','-0.6,8.4,139.25'),f('E1TGT','12.0,10.6,138.8'),18)
cam('OC_CAM_eye_1F_east_end_looking_west',f('E2LOC','11.6,7.6,139.2'),f('E2TGT','0.0,11.2,138.6'),18)
cam('OC_CAM_closeup_1F_east_rug_grey_chairs_table',f('CLLOC','8.75,7.5,138.75'),f('CLTGT','10.3,9.6,138.1'),float(os.environ.get('CLLENS','26')))
sc['oc_state']=json.dumps({'hidden':hidden,'n':len(col.objects)})
print('OC_BUILT',len(col.objects),'hidden',len(hidden))
if SAVE: bpy.ops.wm.save_mainfile(); print('OC_SAVED',len(bpy.data.objects))

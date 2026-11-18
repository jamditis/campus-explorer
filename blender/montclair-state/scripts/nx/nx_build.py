# nx (Oct 30 2026 ~11:40 PM ET, MAIN): (1) 1F fill for the green patch N/NE of the CCOM tower, ONLY east of the slanted CCOM
# exterior wall (ray probe: wall outer face x=-14.39 at y 25.5 -> -13.94 at y 27.5) and under the CCOM roof; the area west of
# that wall (x -17..-14.4) is an unroofed exterior notch and is left as terrain. (2) N classroom whiteboard detail: satin
# aluminium frame, marker tray with 3 markers + eraser, map rail with 2 clips. (3) NX cameras incl. an eye-level shell
# closeup that sees the nw skirting. ALL UNVERIFIED (no photos of these zones).
import bpy, os, json, mathutils, bmesh
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NX_CCOM_tower_N_fill_whiteboard_detail_20261030nx'; sc=bpy.context.scene
MATN=('NX_whiteboard_frame_aluminium_UNVERIFIED','NX_marker_black_UNVERIFIED','NX_marker_blue_UNVERIFIED','NX_marker_red_UNVERIFIED','NX_eraser_felt_UNVERIFIED','NX_map_rail_cork_UNVERIFIED')
def revert():
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    for mn in MATN:
        m=bpy.data.materials.get(mn)
        if m and m.users==0: bpy.data.materials.remove(m)
    for k in ('nx_state','nx_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nx'; o['msu_verified']='UNVERIFIED'
def mat(n,c,r,metal=0.0):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=metal; return m
def addbox(bm,x0,x1,y0,y1,z0,z1):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
def mk(nm,bm,m,layer,shadow=True):
    me=bpy.data.meshes.new(nm); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o=bpy.data.objects.new(nm,me); col.objects.link(o); tag(o,layer); o.visible_shadow=shadow; return o
# ---- (1) N-of-tower fill, east of the slanted wall
dg=bpy.context.evaluated_depsgraph_get(); dn=mathutils.Vector((0,0,-1))
xw=lambda y: -14.39+(y-25.5)*0.225
roofs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('School of Communication and Media roof','School of Communication and Media hip')) or (o.name.startswith('CCOM') and 'roof' in o.name.lower()))]
from mathutils.bvhtree import BVHTree
rbs=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]) for o in roofs]
G=0.25; cells=[]
for j in range(int((28.75-24.0)/G)):
    y0=24.0+j*G; y1=y0+G; yc=(y0+y1)/2
    for i in range(int((-11.0+15.0)/G)):
        x0=-15.0+i*G; x1=x0+G; xc=(x0+x1)/2
        if xc<xw(y1)+0.12: continue
        if not any(b.ray_cast(mathutils.Vector((xc,yc,190)),dn)[0] for b in rbs): continue
        r=sc.ray_cast(dg,mathutils.Vector((xc,yc,142.9)),dn)
        if r[0] and r[4].name.startswith('Terrain') and r[1].z<137.73: cells.append((x0,x1,y0,y1))
bm=bmesh.new()
for (x0,x1,y0,y1) in cells:
    addbox(bm,max(x0-0.02,xw(y1)+0.05),x1+0.02,y0-0.02,y1+0.02,136.9,137.74)
mk('NX 1F fill cells N of the CCOM tower inside the slanted wall (UNVERIFIED)',bm,bpy.data.materials['NV_blocked_out_floor_joints_UNVERIFIED'],'floor')
state['tower_n_cells']=len(cells); print('NX tower-N fill cells',len(cells),cells[:4])
# ---- (2) whiteboard detail (board: x 0.6..5.4, y 17.86..17.88 (face at 17.86), z 138.55..139.75; wall face y 17.9)
al=mat(MATN[0],(0.62,0.63,0.64),0.32,1.0)
X0,X1,Z0,Z1,YF,YW=0.6,5.4,138.55,139.75,17.86,17.895
FW=0.022; FD=0.016
bm=bmesh.new()
addbox(bm,X0-FW,X1+FW,YF-FD,YW,Z1,Z1+FW); addbox(bm,X0-FW,X1+FW,YF-FD,YW,Z0-FW,Z0)
addbox(bm,X0-FW,X0,YF-FD,YW,Z0,Z1); addbox(bm,X1,X1+FW,YF-FD,YW,Z0,Z1)
# marker tray: 7 cm deep, lip 2 cm, end caps
TZ=Z0-FW; addbox(bm,X0+0.3,X1-0.3,YF-0.075,YF-FD,TZ-0.012,TZ-0.004)       # tray floor
addbox(bm,X0+0.3,X1-0.3,YF-0.08,YF-0.075,TZ-0.016,TZ+0.012)               # front lip
addbox(bm,X0+0.3,X1-0.3,YF-FD,YW,TZ-0.03,TZ-0.004)                          # back bracket
for xe in (X0+0.29,X1-0.31): addbox(bm,xe,xe+0.02,YF-0.08,YW,TZ-0.02,TZ+0.014)
# map rail above the board with 2 clips
addbox(bm,X0-FW,X1+FW,YW-0.012,YW,Z1+0.06,Z1+0.11)
for xc in (1.4,4.1): addbox(bm,xc,xc+0.03,YW-0.02,YW-0.012,Z1+0.05,Z1+0.10)
mk('NX N classroom whiteboard frame, marker tray and map rail (UNVERIFIED)',bm,al,'furniture')
bm=bmesh.new(); addbox(bm,X0-FW+0.01,X1+FW-0.01,YW-0.011,YW-0.001,Z1+0.065,Z1+0.105)
mk('NX N classroom map rail cork insert (UNVERIFIED)',bm,mat(MATN[5],(0.42,0.30,0.18),0.9),'furniture')
# markers lying in the tray (along x), eraser
mz=TZ-0.004
def marker(nm,x,c):
    bm=bmesh.new(); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=12,radius1=0.009,radius2=0.009,depth=0.125)
    for v in r['verts']: v.co=mathutils.Vector((x+v.co.z,YF-0.045,mz+0.009+v.co.y*1)) if False else mathutils.Vector((x+v.co.z,YF-0.045+v.co.x,mz+0.009+v.co.y))
    o=mk(nm,bm,mat(nm.split(' (')[0].replace('NX N classroom ','NX_').replace(' ','_')+'_UNVERIFIED' if False else {'k':MATN[1],'b':MATN[2],'r':MATN[3]}[c],{'k':(0.02,0.02,0.02),'b':(0.02,0.05,0.25),'r':(0.4,0.02,0.02)}[c],0.35),'furniture')
    for p in o.data.polygons: p.use_smooth=True
for nm,x,c in (('NX N classroom marker black (UNVERIFIED)',2.1,'k'),('NX N classroom marker blue (UNVERIFIED)',2.32,'b'),('NX N classroom marker red (UNVERIFIED)',3.6,'r')): marker(nm,x,c)
bm=bmesh.new(); addbox(bm,2.75,2.90,YF-0.07,YF-0.02,mz,mz+0.028)
mk('NX N classroom whiteboard eraser (UNVERIFIED)',bm,mat(MATN[4],(0.08,0.08,0.09),0.85),'furniture')
# ---- cameras
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('NX_CAM_aerial_cutaway_oblique_CCOM_from_SW',f('ALOC','-6,8,178'),f('ATGT','-6,19,138'),float(os.environ.get('ALENS','26')))
camcopy('NX_CAM_eye_atrium_looking_west_to_doors','NW_CAM_eye_atrium_looking_west_to_doors')
camcopy('NX_CAM_eye_1F_open_floor_cafe_looking_east','NW_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NX_CAM_closeup_N_classroom_whiteboard_tray_skirting',f('CLLOC','6.3,16.95,138.95'),f('CLTGT','3.4,17.88,138.35'),float(os.environ.get('CLLENS','30')))
sc['nx_state']=json.dumps(state)
sc['nx_note']='nx: 1F fill N of the CCOM tower east of the slanted wall; N classroom whiteboard frame/tray/markers/map rail; NX cameras; UNVERIFIED'
print('NX objects',len(col.objects),'total',len(bpy.data.objects),state)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

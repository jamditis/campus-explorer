# oe (Oct 31 2026 ~6:35 AM ET, MAIN, CCOM atrium): tall wood wall panelling on the atrium N wall (tower face) beside the stair,
# after refs/ccom_google/ccom_epic_interior_28 (full-height veneer panels with narrow reveals on the wall left of the stair, same warm
# wood as the stair side). Extent (x -18.2..-7.4, floor 137.70 to ceiling 146.0) and panel module (9 x 4, ~1.2 x 2.07 m) are estimated
# -> UNVERIFIED. od's round wall handrail is moved 3 mm toward the wall so its rosettes sit on the panel face. SAVE=1 saves, REVERT=1 undoes.
import bpy, os, json, sys, bmesh
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sys.path.insert(0,os.path.abspath('scripts/oa')); import importlib, oa_geo; importlib.reload(oa_geo); G=oa_geo
CN='OE_CCOM_atrium_stair_wall_wood_panelling_20261031oe'; sc=bpy.context.scene; assert len(CN)<=63
HR='OD 1F atrium stair N wall handrail round (UNVERIFIED)'; DY=0.003
def revert():
    st=json.loads(sc.get('oe_state','{}'))
    if st.get('hr_moved'):
        o=bpy.data.objects.get(HR)
        if o: o.location.y-=DY
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    for mm in list(bpy.data.materials):
        if mm.name.startswith('OE_wall') and mm.users==0: bpy.data.materials.remove(mm)
    if 'oe_state' in sc: del sc['oe_state']
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
src=bpy.data.materials['NG_wood_cladding']; W=bpy.data.materials.get('OE_wall_panel_wood_veneer_UNVERIFIED')
if not W:
    W=src.copy(); W.name='OE_wall_panel_wood_veneer_UNVERIFIED'; nt=W.node_tree
    tc=next(n for n in nt.nodes if n.type=='TEX_COORD'); wv=next(n for n in nt.nodes if n.type=='TEX_WAVE')
    for l in list(nt.links):
        if l.from_node==tc: nt.links.remove(l)
    nt.links.new(tc.outputs['Object'],wv.inputs['Vector'])   # object coords: grain does not stretch over the 10.8 x 8.3 m panel field
    W['oe_note']='copy of NG_wood_cladding with Object coords (vertical grain on the XZ wall); UNVERIFIED'
REV=G.pm('OE_wall_panel_reveal_shadow_dark_UNVERIFIED',(0.035,0.028,0.022),0.7)
X0,X1,Z0,Z1=-18.2,-7.4,137.70,146.0; NX,NZ=9,4; g=0.012; YB=16.521; YF=16.503   # wall face y 16.525 (probe), stair clad edge y 16.500
bm=bmesh.new(); pw=(X1-X0)/NX; ph=(Z1-Z0)/NZ
for i in range(NX):
    for j in range(NZ):
        G.box(bm,X0+i*pw+g/2,X0+(i+1)*pw-g/2,YF,YB,Z0+j*ph+(g/2 if j else 0.0),Z0+(j+1)*ph-(g/2 if j<NZ-1 else 0.0))
pan=bpy.data.objects.new('OE atrium N wall wood veneer panels (UNVERIFIED)',G.mesh('OE wall panels',bm)); pan.data.materials.append(W)
bv=pan.modifiers.new('OE bevel','BEVEL'); bv.width=0.003; bv.segments=1
bm=bmesh.new(); G.box(bm,X0,X1,YB-0.002,YB+0.002,Z0,Z1)   # dark backer seen through the reveals
bk=bpy.data.objects.new('OE atrium N wall panel reveal backer (UNVERIFIED)',G.mesh('OE wall panel backer',bm)); bk.data.materials.append(REV)
for o in (pan,bk):
    col.objects.link(o); o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']='interior_finish'
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='oe'; o['msu_verified']='UNVERIFIED (photo-based type, estimated extent/module)'
hr=bpy.data.objects.get(HR); moved=False
if hr: hr.location.y+=DY; moved=True
sc['oe_state']=json.dumps({'hr_moved':moved})
print('OE built',len(col.objects),'hr_moved',moved)
if SAVE: bpy.ops.wm.save_mainfile(); print('OE_SAVED',len(bpy.data.objects))

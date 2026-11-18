# nq (Oct 30 2026 ~4:45 PM ET, MAIN): CCOM interior polish per np 'Next' — ALL UNVERIFIED:
# (a) east daylight card: flat 3.5x emissive white -> soft view gradient (tree/ground band low, pale sky high), lower strength, so the east windows stop blowing out at eye level;
# (b) ceiling smoke detectors in the N classroom + S office (white disc, red LED) — code-typical, UNVERIFIED;
# (c) bevel modifier (NQ_bevel) on the np horn/strobes + pull stations (boxy in close-up);
# (d) blocked-out interior floor under the cutaway where grass showed through inside the CCOM roof footprint (aerial 'grass strip'), UNVERIFIED;
# render-time only (nq_render.py): rooftop exhaust-fan hoods + Roof_vent islands over the CCOM cut region removed for cutaway cams.
import bpy, bmesh, os, json, mathutils, math
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NQ_CCOM_daylight_smoke_bevel_floor_20261030nq'
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('nq_state','{}'))
    for n,(link,objmat) in st.get('slots',{}).items():
        o=bpy.data.objects.get(n)
        if o: s=o.material_slots[0]; s.link='OBJECT'; s.material=bpy.data.materials.get(objmat) if objmat else None; s.link=link
    for n in st.get('bevel',[]):
        o=bpy.data.objects.get(n)
        if o and 'NQ_bevel' in o.modifiers: o.modifiers.remove(o.modifiers['NQ_bevel'])
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                for coll in (bpy.data.meshes,bpy.data.cameras,bpy.data.lights,bpy.data.curves):
                    if d.name in coll and coll[d.name]==d: coll.remove(d); break
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.name.startswith('NQ_') and me.users==0: bpy.data.meshes.remove(me)
    for m in list(bpy.data.materials):
        if m.name.startswith('NQ_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('nq_state','nq_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'slots':{},'bevel':[]}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nq'
def mat(name,c,rough=0.6,emit=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=c; p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=c; p.inputs['Emission Strength'].default_value=emit
    return m
# (a) daylight card gradient
card=bpy.data.objects.get('NG east daylight card behind glass UNVERIFIED')
if card:
    m=bpy.data.materials.new('NQ_east_view_gradient_UNVERIFIED'); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    tc=nt.nodes.new('ShaderNodeTexCoord'); sp=nt.nodes.new('ShaderNodeSeparateXYZ'); cr=nt.nodes.new('ShaderNodeValToRGB')
    em=nt.nodes.new('ShaderNodeEmission'); outn=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(tc.outputs['Generated'],sp.inputs[0]); nt.links.new(sp.outputs['Z'],cr.inputs[0])
    e=cr.color_ramp.elements; e[0].position=0.0; e[0].color=(0.16,0.19,0.15,1); e[1].position=0.24; e[1].color=(0.30,0.34,0.30,1)
    e3=e.new(0.30); e3.color=(0.62,0.68,0.74,1); e4=e.new(1.0); e4.color=(0.70,0.80,0.95,1)
    nt.links.new(cr.outputs['Color'],em.inputs['Color']); em.inputs['Strength'].default_value=1.6
    nt.links.new(em.outputs[0],outn.inputs['Surface'])
    sl=card.material_slots[0]; state['slots'][card.name]=(sl.link,sl.material.name if (sl.link=='OBJECT' and sl.material) else None); sl.link='OBJECT'; sl.material=m
# (b) smoke detectors
def cylbm(bm,x,y,z0,z1,r,seg=24):
    res=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r*0.92,depth=z1-z0)
    bmesh.ops.translate(bm,verts=res['verts'],vec=(x,y,(z0+z1)/2))
wh=mat('NQ_smoke_detector_white_UNVERIFIED',(0.86,0.86,0.84,1),0.45); led=mat('NQ_smoke_detector_led_red_UNVERIFIED',(0.9,0.05,0.03,1),0.3,emit=2.0)
bm=bmesh.new(); res=bmesh.ops.create_cone(bm,cap_ends=True,segments=28,radius1=0.068,radius2=0.060,depth=0.040); bmesh.ops.translate(bm,verts=res['verts'],vec=(0,0,-0.020))
res=bmesh.ops.create_cone(bm,cap_ends=True,segments=20,radius1=0.040,radius2=0.036,depth=0.008); bmesh.ops.translate(bm,verts=res['verts'],vec=(0,0,-0.044))
me=bpy.data.meshes.new('NQ_smoke_detector_UNVERIFIED'); bm.to_mesh(me); bm.free(); me.materials.append(wh)
for o in me.polygons: o.use_smooth=True
bm=bmesh.new(); res=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.0035,radius2=0.0035,depth=0.003); bmesh.ops.translate(bm,verts=res['verts'],vec=(0.050,0,-0.0415))
meL=bpy.data.meshes.new('NQ_smoke_detector_led_UNVERIFIED'); bm.to_mesh(meL); bm.free(); meL.materials.append(led)
SD=[('N classroom',2.448,15.909,140.888),('N classroom',5.496,15.909,140.888),('S office',2.248,5.229,140.888),('S office',5.296,5.229,140.888)]  # tile centres of the no 2x2 ft grids
for i,(nm,x,y,z) in enumerate(SD):
    ob=bpy.data.objects.new('NQ smoke detector %s %d (UNVERIFIED)'%(nm,i),me); ob.location=(x,y,z); col.objects.link(ob); tag(ob,'life_safety'); ob.visible_shadow=False
    obL=bpy.data.objects.new('NQ smoke detector %s %d LED (UNVERIFIED)'%(nm,i),meL); obL.location=(x,y,z); col.objects.link(obL); tag(obL,'life_safety'); obL.visible_shadow=False
# (c) bevels on strobes + pull stations
for o in bpy.data.objects:
    if o.name.startswith(('NP horn-strobe','NP manual pull station')) and o.type=='MESH':
        b=o.modifiers.new('NQ_bevel','BEVEL'); b.width=0.006; b.segments=2; b.limit_method='ANGLE'; b.harden_normals=False
        state['bevel'].append(o.name)
# (d) blocked-out floor where the cutaway shows ground inside the CCOM roof footprint
dg=bpy.context.evaluated_depsgraph_get()
roofs=set(o.name for o in bpy.data.objects if o.name.startswith('School of Communication and Media roof'))
hide_tmp=[o for o in bpy.data.objects if o.name.startswith('School of Communication and Media roof')]
cells=[]; S=1.0
from mathutils.bvhtree import BVHTree
rb=[(o,BVHTree.FromObject(o,dg),o.matrix_world.inverted()) for o in bpy.data.objects if o.name in roofs and o.type=='MESH']
def roofz(x,y):
    for o,t,Mi in rb:
        org=Mi@mathutils.Vector((x,y,175.0)); d=(Mi.to_3x3()@mathutils.Vector((0,0,-1))).normalized()
        hit=t.ray_cast(org,d)
        if hit[0] is not None: return (o.matrix_world@hit[0]).z
    return None
for ix in range(-21,14):
    for iy in range(-14,26):
        x=ix+0.5; y=iy+0.5; rz=roofz(x,y)
        if rz is None or any(roofz(x+dx,y+dy) is None for dx,dy in ((-0.7,-0.7),(0.7,-0.7),(0.7,0.7),(-0.7,0.7))): continue
        h2,l2,n2,i2,ob2,mm2=sc.ray_cast(dg,(x,y,rz-0.3),(0,0,-1))
        if h2 and ob2.name.startswith('Terrain_LiDAR') and l2.z<137.3: cells.append((x,y,l2.z,ob2.name))
print('NQ gap cells',len(cells), set(c[3] for c in cells))
if cells:
    fl=mat('NQ_blocked_out_interior_floor_UNVERIFIED',(0.42,0.41,0.39,1),0.7)
    bm=bmesh.new(); ZT=137.40
    for x,y,z,_ in cells:
        r=bmesh.ops.create_cube(bm,size=1.0)
        for v in r['verts']: v.co=mathutils.Vector((x+v.co.x*S,y+v.co.y*S,(ZT+z-0.05)/2+v.co.z*(ZT-z+0.05)))
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.001)
    inner=[f for f in bm.faces if len(set(f.verts))<3]
    me2=bpy.data.meshes.new('NQ_blocked_out_floor'); bm.to_mesh(me2); bm.free(); me2.materials.append(fl)
    ob=bpy.data.objects.new('NQ blocked-out interior floor under CCOM roof (UNVERIFIED)',me2); col.objects.link(ob); tag(ob,'floor')
    print('NQ floor z',min(c[2] for c in cells),max(c[2] for c in cells),'xy',min(c[0] for c in cells),max(c[0] for c in cells),min(c[1] for c in cells),max(c[1] for c in cells))
# cameras
def cam(n,loc,tgt,lens_):
    c=bpy.data.cameras.new(n); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
cam('NQ_CAM_aerial_cutaway_studio_atrium_oblique',(-3.0,-22.0,178.0),(-9.0,4.0,138.0),28)
cam('NQ_CAM_eye_1F_open_floor_looking_east_windows',(-1.2,10.6,139.3),(10.0,10.4,139.6),18)
cam('NQ_CAM_eye_1F_open_floor_east_end_looking_west',(11.3,9.0,139.2),(-6.0,11.0,139.8),18)
cam('NQ_CAM_closeup_N_wall_strobe_bevel',(2.70,13.25,139.70),(3.0,13.93,139.83),35)
cam('NQ_CAM_closeup_N_classroom_smoke_detector',(2.05,15.2,139.6),(2.448,15.909,140.86),24)
sc['nq_state']=json.dumps(state)
sc['nq_note']='nq: east view gradient, room smoke detectors, strobe/pull bevels, blocked-out floor under cutaway gap; ALL UNVERIFIED'
print('NQ objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

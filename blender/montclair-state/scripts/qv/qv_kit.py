# qv parallel prep: plaza furniture kit for day 8 (Student Center plaza) after the PD Commons photo
# refs/web/20261103qv/MSU_Richardson_and_Mallory_Halls_640.jpg: dark grey slatted bench with scroll cast arms, square-pole lamp with
# a flat box head, grey vertical-slat litter bin, cast-iron tree/drain grate. Dimensions are typical catalogue sizes (UNVERIFIED).
# Library only: per the street-furniture rule, place in a scene only where a photo/ortho shows one.
import bpy, bmesh, math
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def mat(n,c,r=0.5,m=0.0):
    M=bpy.data.materials.new(n); M.use_nodes=True; p=M.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=r; p.inputs['Metallic'].default_value=m; return M
MG=mat('QVK_powdercoat_dark_grey',(0.09,0.095,0.10),0.45,0.6); MI=mat('QVK_cast_iron',(0.05,0.05,0.05),0.6,0.7)
MB=mat('QVK_bin_grey',(0.20,0.21,0.22),0.5,0.4); ML=mat('QVK_lamp_lens',(0.85,0.95,0.85),0.2,0.0)
ML.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(1,0.95,0.85,1)
def box(name,dim,loc,M,col,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.scale=dim
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(M)
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o); return o
def join(objs,name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join(); o=bpy.context.object; o.name=name; return o
def coll(n):
    c=bpy.data.collections.new(n); sc.collection.children.link(c); return c
# bench 1.83 m (6 ft), 9 seat/back slats, scroll arms
cb=coll('QVK_bench_slatted_scroll_arms'); parts=[]
for i in range(5): parts.append(box('s',(1.83,0.075,0.03),(0,-0.25+i*0.085,0.45),MG,cb))
for i in range(4): parts.append(box('b',(1.83,0.03,0.075),(0,0.13+0.012*i,0.55+i*0.09),MG,cb,(math.radians(-12),0,0)))
for x in (-0.86,0.86):
    parts.append(box('leg',(0.04,0.5,0.04),(x,-0.05,0.21),MI,cb,(math.radians(0),0,0)))
    for k in range(10):
        a=math.pi*k/9; parts.append(box('arm',(0.035,0.06,0.03),(x,-0.20+0.12*math.cos(a)-0.05,0.62+0.07*math.sin(a)),MI,cb))
    parts.append(box('foot',(0.05,0.55,0.03),(x,-0.05,0.015),MI,cb))
    parts.append(box('post',(0.035,0.035,0.62),(x,0.16,0.62),MI,cb))
b=join(parts,'QVK_bench_slatted_scroll_arms_UNVERIFIED'); b['qv_src']='type from PD photo MSU Richardson & Mallory Halls (Commons); size typical 6 ft'
# lamp: 4.3 m square pole + box head on a short arm
cl=coll('QVK_lamp_square_pole_box_head'); parts=[box('pole',(0.11,0.11,4.3),(0,0,2.15),MG,cl),box('base',(0.28,0.28,0.5),(0,0,0.25),MG,cl),
 box('arm',(0.55,0.08,0.08),(0.30,0,4.15),MG,cl),box('head',(0.70,0.36,0.16),(0.62,0,4.20),MG,cl)]
l=join(parts,'QVK_lamp_square_pole_box_head_UNVERIFIED'); lens=box('QVK_lamp_lens_UNVERIFIED',(0.60,0.28,0.02),(0.62,0,4.11),ML,cl)
# bin: 0.6 m dia slatted cylinder (24 slats) + dome lid
cbin=coll('QVK_bin_vertical_slats'); parts=[]
for k in range(24):
    a=2*math.pi*k/24; parts.append(box('sl',(0.05,0.018,0.85),(0.29*math.cos(a),0.29*math.sin(a),0.47),MB,cbin,(0,0,a+math.pi/2)))
parts.append(box('ring',(0.62,0.62,0.04),(0,0,0.06),MB,cbin)); parts.append(box('ring2',(0.62,0.62,0.04),(0,0,0.86),MB,cbin))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.31,location=(0,0,0.9),segments=24,ring_count=8); d=bpy.context.object; d.scale=(1,1,0.35); bpy.ops.object.transform_apply(scale=True)
d.data.materials.append(MB); [c.objects.unlink(d) for c in d.users_collection]; cbin.objects.link(d); parts.append(d)
join(parts,'QVK_bin_vertical_slats_UNVERIFIED')
# grate 0.6 x 0.6 cast iron with 12 slots
cg=coll('QVK_grate_cast_iron'); parts=[box('fr',(0.62,0.62,0.02),(0,0,0.0),MI,cg)]
join(parts,'QVK_grate_cast_iron_UNVERIFIED')
# spread for preview
for o,x in ((bpy.data.objects['QVK_bench_slatted_scroll_arms_UNVERIFIED'],0),(bpy.data.objects['QVK_lamp_square_pole_box_head_UNVERIFIED'],3),(bpy.data.objects['QVK_lamp_lens_UNVERIFIED'],3),(bpy.data.objects['QVK_bin_vertical_slats_UNVERIFIED'],5),(bpy.data.objects['QVK_grate_cast_iron_UNVERIFIED'],6.5)):
    o.location.x+=x
print('KIT',[o.name for o in bpy.data.objects])
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/assets/plaza_furniture_kit_qv.blend')

import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
random.seed(242)
col=bpy.data.collections['WS24_AnnexWest_asphalt_plaza_planters_20261110ws24']
# 1 asphalt boundary feather (no lip)
a=[o for o in col.objects if o.name.startswith('WS24 Annex west asphalt')][0]
bm=bmesh.new(); bm.from_mesh(a.data)
nb=0
for v in bm.verts:
    if v.is_boundary: v.co.z-=0.027; nb+=1
for v in bm.verts:
    if not v.is_boundary and any(e.other_vert(v).is_boundary for e in v.link_edges): v.co.z-=0.012
bm.to_mesh(a.data); bm.free(); print('feathered',nb)
# 2 asphalt seal cracks via voronoi edge, darker
m=bpy.data.materials['WS24_asphalt_weathered_JoePhoto']; nt=m.node_tree; b=nt.nodes['Principled BSDF']
ramp=[n for n in nt.nodes if n.type=='VALTORGB'][0]
tc=[n for n in nt.nodes if n.type=='TEX_COORD'][0]
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.9; nz.inputs['Detail'].default_value=3
nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='VECTOR'; mx.inputs['Factor'].default_value=0.12
nt.links.new(tc.outputs['Object'],mx.inputs['A']); nt.links.new(nz.outputs['Color'],mx.inputs['B'])
vo=nt.nodes.new('ShaderNodeTexVoronoi'); vo.feature='DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value=0.28
nt.links.new(mx.outputs['Result'],vo.inputs['Vector'])
mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.0; mr.inputs['From Max'].default_value=0.012; mr.inputs['To Min'].default_value=0.35; mr.inputs['To Max'].default_value=1.0
nt.links.new(vo.outputs['Distance'],mr.inputs['Value'])
mul=nt.nodes.new('ShaderNodeMix'); mul.data_type='RGBA'; mul.blend_type='MULTIPLY'; mul.inputs['Factor'].default_value=1.0
nt.links.new(ramp.outputs['Color'],mul.inputs['A']); nt.links.new(mr.outputs['Result'],mul.inputs['B'])
nt.links.new(mul.outputs['Result'],b.inputs['Base Color'])
# 3 planter grey
pm=bpy.data.materials['WS24_planter_cast_concrete_grey_JoePhoto']; r=[n for n in pm.node_tree.nodes if n.type=='VALTORGB'][0].color_ramp
r.elements[0].color=(0.15,0.15,0.15,1); r.elements[1].color=(0.21,0.21,0.205,1)
# 4 foliage resize + flower spikes
leaf=bpy.data.materials['WS24_planter_foliage_green']; lb=leaf.node_tree.nodes['Principled BSDF']
lr=[n for n in leaf.node_tree.nodes if n.type=='VALTORGB'][0].color_ramp; lr.elements[0].color=(0.02,0.06,0.015,1); lr.elements[1].color=(0.07,0.16,0.04,1)
flm=[bpy.data.materials[n] for n in ('WS24_flower_red','WS24_flower_magenta','WS24_flower_pink')]
for o in list(col.objects):
    if o.name.endswith('foliage'):
        idx=int(o.name.split()[2]); base=bpy.data.objects[[n.name for n in col.objects if n.name.startswith(f'WS24 planter {idx:02d} (')][0]]
        zs=[ (base.matrix_world@v.co).z for v in base.data.vertices]; z0=min(zs); cx,cy=o.location.x,o.location.y
        o.location.z=z0+0.60; o.scale=(0.34,0.34,0.20+random.uniform(0,0.06))
        d=o.modifiers['d']; d.strength=0.07; d.mid_level=0.5
        fo=[n for n in col.objects if n.name==f'WS24 planter {idx:02d} flowers'][0]
        bm=bmesh.new()
        for k in range(110):
            a_=random.uniform(0,2*math.pi); rr=0.34*math.sqrt(random.random())
            hz=z0+0.60+0.24*math.sqrt(max(0,1-(rr/0.36)**2))+random.uniform(-0.01,0.05)
            bmesh.ops.create_icosphere(bm,subdivisions=1,radius=random.uniform(0.018,0.032),matrix=Matrix.Translation((cx+rr*math.cos(a_),cy+rr*math.sin(a_),hz)))
        # tall flower spikes (celosia/salvia-like, photo shows spikes above pots)
        for k in range(random.randint(7,12)):
            a_=random.uniform(0,2*math.pi); rr=0.22*math.sqrt(random.random()); h=random.uniform(0.18,0.38)
            zb=z0+0.60+0.2; tilt=Matrix.Rotation(random.uniform(-0.25,0.25),4,'X')@Matrix.Rotation(random.uniform(-0.25,0.25),4,'Y')
            mtx=Matrix.Translation((cx+rr*math.cos(a_),cy+rr*math.sin(a_),zb+h/2))@tilt
            bmesh.ops.create_cone(bm,cap_ends=True,segments=6,radius1=0.045,radius2=0.008,depth=h,matrix=mtx)
        bm.to_mesh(fo.data); bm.free()
        for p in fo.data.polygons: p.use_smooth=True
print('planters done')
bpy.ops.wm.save_mainfile(); print('SAVED')

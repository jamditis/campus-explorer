# td (Nov 4 2026 ~5:45 PM ET, MAIN, day 8 Student Center north side). ALL UNVERIFIED, reversible (REVERT=1).
# (1) Quad Road + Webster Road get a darker road-asphalt copy TD_asphalt_road_UNVERIFIED (sg eye view read pale/concrete-like); lot keeps SF asphalt.
# (2) Oil stains: copy TD_oil_stain_soft_UNVERIFIED with a noise-warped gradient so the drips read as irregular blots, not round discs.
import bpy, os
REV=os.environ.get('REVERT')=='1'
ROADS=['SG_QuadRoad_full_313028548_549_UNVERIFIED','SG_WebsterRoad_313028543_UNVERIFIED']
STAIN='SG_Lot38_oil_stains_UNVERIFIED'; CURB='SG_Lot38_curbs_UNVERIFIED'
# (3) curb control joints every 3.0 m (typical, UNVERIFIED): per-face run direction attribute + shader groove.
def revert():
    for n in ROADS+[STAIN]:
        o=bpy.data.objects.get(n)
        if o and 'td_oldmat' in o:
            m0=bpy.data.materials[o['td_oldmat']]; o.data.materials[0]=m0; del o['td_oldmat']
    c=bpy.data.objects.get(CURB)
    if c:
        if 'td_oldmat' in c: c.data.materials[0]=bpy.data.materials[c['td_oldmat']]; del c['td_oldmat']
        a=c.data.attributes.get('td_curbdir')
        if a: c.data.attributes.remove(a)
    for n in ('TD_asphalt_road_UNVERIFIED','TD_oil_stain_soft_UNVERIFIED','TD_curb_joints_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('TD reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
# (1)
src=bpy.data.materials['SF_asphalt_worn_UNVERIFIED']; m=src.copy(); m.name='TD_asphalt_road_UNVERIFIED'
nt=m.node_tree; cr=nt.nodes['Color Ramp'].color_ramp
for e in cr.elements:
    c=e.color; e.color=(c[0]*0.58,c[1]*0.58,c[2]*0.60,1)
nt.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=0.12
nt.nodes['Bump'].inputs['Strength'].default_value=0.22
for n in ROADS:
    o=bpy.data.objects[n]; o['td_oldmat']=o.data.materials[0].name; o.data.materials[0]=m
print('TD road mat', [tuple(round(x,3) for x in e.color[:3]) for e in cr.elements])
# (2)
s0=bpy.data.materials['SG_oil_stain_UNVERIFIED']; s=s0.copy(); s.name='TD_oil_stain_soft_UNVERIFIED'; nt=s.node_tree
tc=nt.nodes['Texture Coordinate']; vm=nt.nodes['Vector Math']
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.2; nz.inputs['Detail'].default_value=3.0; nz.inputs['Distortion'].default_value=0.6
sub=nt.nodes.new('ShaderNodeVectorMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=(0.5,0.5,0.5)
scl=nt.nodes.new('ShaderNodeVectorMath'); scl.operation='SCALE'; scl.inputs['Scale'].default_value=0.45
add=nt.nodes.new('ShaderNodeVectorMath'); add.operation='ADD'
nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(nz.outputs['Color'],sub.inputs[0]); nt.links.new(sub.outputs[0],scl.inputs[0])
nt.links.new(tc.outputs['UV'],add.inputs[0]); nt.links.new(scl.outputs[0],add.inputs[1]); nt.links.new(add.outputs[0],vm.inputs[0])
bs=nt.nodes['Principled BSDF']; bs.inputs['Specular IOR Level'].default_value=0.15; bs.inputs['Roughness'].default_value=0.8
o=bpy.data.objects[STAIN]; o['td_oldmat']=o.data.materials[0].name; o.data.materials[0]=s
# (3)
import math
c=bpy.data.objects[CURB]; me=c.data; V=me.vertices
a=me.attributes.new('td_curbdir','FLOAT_VECTOR','FACE')
for f in me.polygons:
    best=(0,(1,0))
    for i in range(len(f.vertices)):
        p=V[f.vertices[i]].co; q=V[f.vertices[(i+1)%len(f.vertices)]].co; dx,dy=q.x-p.x,q.y-p.y; L=math.hypot(dx,dy)
        if L>best[0]: best=(L,(dx/L,dy/L))
    a.data[f.index].vector=(best[1][0],best[1][1],0)
c0=me.materials[0]; cm=c0.copy(); cm.name='TD_curb_joints_UNVERIFIED'; nt=cm.node_tree
at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='td_curbdir'
ge=nt.nodes.new('ShaderNodeNewGeometry'); tx=nt.nodes.new('ShaderNodeTexCoord')
dp=nt.nodes.new('ShaderNodeVectorMath'); dp.operation='DOT_PRODUCT'
nt.links.new(tx.outputs['Object'],dp.inputs[0]); nt.links.new(at.outputs['Vector'],dp.inputs[1])
dv=nt.nodes.new('ShaderNodeMath'); dv.operation='DIVIDE'; dv.inputs[1].default_value=3.0; nt.links.new(dp.outputs['Value'],dv.inputs[0])
fr=nt.nodes.new('ShaderNodeMath'); fr.operation='FRACT'; nt.links.new(dv.outputs[0],fr.inputs[0])
d1=nt.nodes.new('ShaderNodeMath'); d1.operation='SUBTRACT'; d1.inputs[1].default_value=0.5; nt.links.new(fr.outputs[0],d1.inputs[0])
ab=nt.nodes.new('ShaderNodeMath'); ab.operation='ABSOLUTE'; nt.links.new(d1.outputs[0],ab.inputs[0])
gt=nt.nodes.new('ShaderNodeMath'); gt.operation='GREATER_THAN'; gt.inputs[1].default_value=0.4958; nt.links.new(ab.outputs[0],gt.inputs[0])
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['B'].default_value=(0.35,0.34,0.33,1)
bs=nt.nodes['Principled BSDF']; crn=nt.nodes['Color Ramp']
nt.links.new(gt.outputs[0],mx.inputs['Factor']); nt.links.new(crn.outputs['Color'],mx.inputs['A']); nt.links.new(mx.outputs['Result'],bs.inputs['Base Color'])
c['td_oldmat']=c0.name; me.materials[0]=cm
print('TD curb joints faces',len(me.polygons))
for mm in (src,s0,c0): mm.use_fake_user=True
print('TD applied')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

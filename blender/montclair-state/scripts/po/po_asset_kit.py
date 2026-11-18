# po background: assets/rainwater_roof_kit_po.blend — box gutter (1 m, array-ready), downpipe (3 m) with strap + gooseneck + shoe,
# RTU on curb (2.6x1.6 m), roof drain, and the PO seamed-membrane material (world-axis seams; rotate the Vector Rotate angle per building).
import bpy, bmesh
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(n,c,metal=0.0,rough=0.5):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Metallic'].default_value=metal; b.inputs['Roughness'].default_value=rough; return m
bronze=mat('PO_kit_dark_bronze',(0.06,0.045,0.035),0.5,0.45); galv=mat('PO_kit_galv_grey',(0.47,0.48,0.48),0.6,0.45); dark=mat('PO_kit_dark_metal',(0.05,0.05,0.055),0.4,0.5)
def obj(name,boxes,mats):
    bm=bmesh.new()
    for (cx,cy,cz),(sx,sy,sz),mi in boxes:
        r=bmesh.ops.create_cube(bm,size=1.0)['verts']
        for v in r: v.co=Vector((cx+v.co.x*sx,cy+v.co.y*sy,cz+v.co.z*sz))
        for f in bm.faces:
            if all(v in r for v in f.verts): f.material_index=mi
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o); o.asset_mark(); o.asset_data.description='po kit (UNVERIFIED generic); origin at mount point'; return o
obj('PO_kit_box_gutter_1m',[((0.5,0,0.065),(1.0,0.13,0.13),0)],[bronze])
pipe=[((0,0,1.5),(0.1,0.1,3.0),0),((0,0,1.5),(0.13,0.13,0.05),0),((0,0,2.9),(0.13,0.13,0.05),0),((0,-0.2,3.05),(0.09,0.4,0.09),0),((0,0.12,0.12),(0.12,0.25,0.25),0)]
obj('PO_kit_downpipe_3m_strapped',pipe,[bronze])
rtu=[((0,0,0.14),(2.9,1.9,0.32),0),((0,0,0.825),(2.6,1.6,1.05),0),((0.57,0,1.38),(0.99,1.12,0.06),1),((0,0.82,0.8),(1.82,0.03,0.5),1),((0,-0.82,0.8),(1.82,0.03,0.5),1),((-1.9,0,0.125),(1.2,0.25,0.25),0)]
obj('PO_kit_RTU_on_curb_2p6m',rtu,[galv,dark])
obj('PO_kit_roof_drain',[((0,0,0.005),(0.7,0.7,0.02),0),((0,0,0.045),(0.28,0.28,0.09),0)],[dark])
# membrane material copied by recipe
m=bpy.data.materials.new('PO_kit_membrane_seamed'); m.use_nodes=True; m.asset_mark(); m.asset_data.description='seamed single-ply membrane: 3 m roll laps + 12 m end laps, ponding tone patches; set Vector Rotate angle = -building angle'
nt=m.node_tree; N=nt.nodes; L=nt.links; bs=N['Principled BSDF']; bs.inputs['Roughness'].default_value=0.82
geo=N.new('ShaderNodeNewGeometry'); vr=N.new('ShaderNodeVectorRotate'); vr.rotation_type='Z_AXIS'; L.new(geo.outputs['Position'],vr.inputs['Vector'])
sx=N.new('ShaderNodeSeparateXYZ'); L.new(vr.outputs['Vector'],sx.inputs[0])
def M(op,a,b=None):
    n=N.new('ShaderNodeMath'); n.operation=op
    for i,v in enumerate((a,b)):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: L.new(v,n.inputs[i])
    return n.outputs[0]
s1=M('LESS_THAN',M('ABSOLUTE',M('SUBTRACT',M('FRACT',M('DIVIDE',sx.outputs['X'],3.0)),0.5)),0.014)
s2=M('LESS_THAN',M('ABSOLUTE',M('SUBTRACT',M('FRACT',M('DIVIDE',sx.outputs['Y'],12.0)),0.5)),0.004)
sm=M('MAXIMUM',s1,s2)
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.09; L.new(geo.outputs['Position'],nz.inputs['Vector'])
cr=N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'],cr.inputs[0]); cr.color_ramp.elements[0].position=0.42; cr.color_ramp.elements[0].color=(0.2,0.198,0.192,1); cr.color_ramp.elements[1].position=0.62; cr.color_ramp.elements[1].color=(0.34,0.34,0.335,1)
mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; L.new(M('MULTIPLY',sm,0.6),mx.inputs['Factor']); L.new(cr.outputs['Color'],mx.inputs[6]); mx.inputs[7].default_value=(0.09,0.09,0.09,1); L.new(mx.outputs[2],bs.inputs['Base Color'])
bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.25; bp.inputs['Distance'].default_value=0.01; L.new(sm,bp.inputs['Height']); L.new(bp.outputs['Normal'],bs.inputs['Normal'])
m.use_fake_user=True
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/assets/rainwater_roof_kit_po.blend'); print('KIT_SAVED',[o.name for o in bpy.data.objects])

# ws49: far street-tree crowns read as smooth pale balls (ws48 review). Rebuild the shared MID proto mesh as a lumpy
# crown + short trunk, and retone its material to the scene's autumn palette with clump shading. Affects the 233 MID_stree
# objects (Oct 15) and the 136 WS48 band instances (all share this mesh). Idempotent.
import bpy, bmesh, math, os
from mathutils import Vector, noise
p=bpy.data.objects['MID_street_tree_proto_20261015ag']; me=p.data; m=me.materials[0]
if me.get('ws49'): print('C49 already'); raise SystemExit
bm=bmesh.new(); bmesh.ops.create_icosphere(bm,subdivisions=4,radius=1.0)
for v in bm.verts:
    d=v.co.normalized(); k=1+0.22*noise.noise(d*2.2+Vector((3.1,1.7,0.4)))+0.05*noise.noise(d*5.0)
    if d.z<-0.3: k*=0.85+0.15*(1+d.z)   # flatter, tucked underside
    v.co=d*k*0.8+Vector((0,0,0.45))
for f in bm.faces: f.material_index=0
r=bmesh.ops.create_cone(bm,cap_ends=True,segments=6,radius1=0.065,radius2=0.045,depth=0.6)
for v in r['verts']: v.co.z+=-0.72+0.30
tf=set(f for v in r['verts'] for f in v.link_faces)
for f in tf: f.material_index=1
bm.to_mesh(me); bm.free()
for poly in me.polygons: poly.use_smooth=True
bark=bpy.data.materials.get('WS49_far_trunk') or bpy.data.materials.new('WS49_far_trunk'); bark.use_nodes=True
bark.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.035,0.027,0.02,1); bark.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.95
if len(me.materials)<2: me.materials.append(bark)
nt=m.node_tree; N=nt.nodes; L=nt.links
r=N['ah_ramp'].color_ramp; r.interpolation='CONSTANT'
while len(r.elements)>1: r.elements.remove(r.elements[-1])
pal=[(0.0,(0.035,0.06,0.025)),(0.28,(0.085,0.085,0.03)),(0.5,(0.30,0.20,0.04)),(0.74,(0.40,0.13,0.03)),(0.93,(0.27,0.06,0.03))]
r.elements[0].position=0; r.elements[0].color=(*pal[0][1],1)
for pos,c in pal[1:]: e=r.elements.new(pos); e.color=(*c,1)
bs=N['Principled BSDF']; bs.inputs['Roughness'].default_value=0.85
if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value=0.15
tc=N.new('ShaderNodeTexCoord'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=4.0; nz.inputs['Detail'].default_value=3
mr=N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value=0.55; mr.inputs['To Max'].default_value=1.12
mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
L.new(tc.outputs['Object'],nz.inputs['Vector']); L.new(nz.outputs['Fac'],mr.inputs['Value'])
L.new(N['ah_ramp'].outputs['Color'],mx.inputs['A']); L.new(mr.outputs['Result'],mx.inputs['B'])
cm=N.new('ShaderNodeCombineColor'); L.new(mr.outputs['Result'],cm.inputs[0]); L.new(mr.outputs['Result'],cm.inputs[1]); L.new(mr.outputs['Result'],cm.inputs[2])
L.new(cm.outputs[0],mx.inputs['B'])
L.new(mx.outputs['Result'],bs.inputs['Base Color'])
me['ws49']=1
print('C49 done verts',len(me.vertices),'mats',[x.name for x in me.materials])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('C49 saved')

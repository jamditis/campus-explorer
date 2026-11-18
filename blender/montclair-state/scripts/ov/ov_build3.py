# ov (C): the OSM walks read near-white in sun at eye level. Footpaths_OSM object slot 0 swapped to a copy of
# OQ_Paving_concrete_east_tone_UNVERIFIED (OV_Paving_concrete_walk_tone_UNVERIFIED) with a MULTIPLY toward weathered concrete grey
# (TONE) x large-scale noise (0.86-1.0) before Base Color. OQ material kept (fake user). ALL UNVERIFIED (visual choice). REVERT=1 undoes.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
OQ='OQ_Paving_concrete_east_tone_UNVERIFIED'; NM='OV_Paving_concrete_walk_tone_UNVERIFIED'
ob=bpy.data.objects['Footpaths_OSM']; om=bpy.data.materials[OQ]
s0=ob.material_slots[0]
if s0.material and s0.material.name==NM: s0.material=om
x=bpy.data.materials.get(NM)
if x: bpy.data.materials.remove(x)
if 'UNVERIFIED_ov_tone' in ob: del ob['UNVERIFIED_ov_tone']
if REV:
    om.use_fake_user=bool(om.get('ov_prev_fake',0))
    if 'ov_prev_fake' in om: del om['ov_prev_fake']
    print('REVERTED3')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
TONE=tuple(float(v) for v in os.environ.get('TONE','0.80,0.79,0.75').split(','))
om['ov_prev_fake']=int(om.use_fake_user); om.use_fake_user=True
m=om.copy(); m.name=NM; nt=m.node_tree
p=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; lk=p.inputs['Base Color'].links[0]; src=lk.from_socket
mul=nt.nodes.new('ShaderNodeMix'); mul.data_type='RGBA'; mul.blend_type='MULTIPLY'; mul.name='OV_walk_tone'
mul.inputs[0].default_value=1.0
A=[s for s in mul.inputs if s.identifier=='A_Color'][0]; Bs=[s for s in mul.inputs if s.identifier=='B_Color'][0]
nt.links.new(src,A)
tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.18; nz.inputs['Detail'].default_value=3.0
nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.35; mr.inputs['From Max'].default_value=0.65
mr.inputs['To Min'].default_value=0.86; mr.inputs['To Max'].default_value=1.0; nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
mm=nt.nodes.new('ShaderNodeMix'); mm.data_type='RGBA'; mm.blend_type='MULTIPLY'; mm.inputs[0].default_value=1.0
mA=[s for s in mm.inputs if s.identifier=='A_Color'][0]; mB=[s for s in mm.inputs if s.identifier=='B_Color'][0]
mA.default_value=(*TONE,1.0)
cmb=nt.nodes.new('ShaderNodeCombineColor'); [nt.links.new(mr.outputs[0],cmb.inputs[i]) for i in range(3)]
nt.links.new(cmb.outputs[0],mB)
nt.links.new(mm.outputs[2],Bs)
nt.links.new([o for o in mul.outputs if o.identifier=='Result_Color'][0],p.inputs['Base Color'])
s0.material=m; ob['UNVERIFIED_ov_tone']='walk tone %s x noise 0.86-1.0'%(TONE,)
print('BUILT3',s0.material.name)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

# qq_roof: Richardson flat roof read as one blank white slab in the S oblique. Tone the membrane (QP_Richardson_roof_membrane)
# to a weathered light grey with 1 m sheet laps (seam lines along the building axis, -23.7 deg), ponding/dirt stains, and
# tone the penthouse/tower tops slightly via a separate mid-grey cap material is NOT done (towers stay white per the slides).
# UNVERIFIED (no current roof photo; 2020 ortho shows a light roof). REVERT=1 removes the QQR_ nodes and restores the inputs.
import bpy, os, json
R=os.environ.get('REVERT')=='1'
m=bpy.data.materials['QP_Richardson_roof_membrane']; nt=m.node_tree; b=nt.nodes['Principled BSDF']
for n in [n for n in nt.nodes if n.name.startswith('QQR_')]: nt.nodes.remove(n)
if R:
    if 'qq_prev' in m:
        p=json.loads(m['qq_prev']); b.inputs['Base Color'].default_value=p['bc']; b.inputs['Roughness'].default_value=p['r']; del m['qq_prev']
    print('QQR reverted')
else:
    if 'qq_prev' not in m: m['qq_prev']=json.dumps({'bc':list(b.inputs['Base Color'].default_value),'r':b.inputs['Roughness'].default_value})
    N=nt.nodes; L=nt.links.new
    def nn(t,name): x=N.new(t); x.name=name; x.label=name; return x
    tc=nn('ShaderNodeTexCoord','QQR_tc'); mp=nn('ShaderNodeMapping','QQR_map'); mp.inputs['Rotation'].default_value[2]=0.4136  # 23.7 deg
    L(tc.outputs['Object'],mp.inputs['Vector'])
    wv=nn('ShaderNodeTexWave','QQR_laps'); wv.wave_type='BANDS'; wv.bands_direction='Y'; wv.wave_profile='SAW'; wv.inputs['Scale'].default_value=1.0/ (1.0*6.2832)*6.2832/1.0
    wv.inputs['Scale'].default_value=0.159; wv.inputs['Distortion'].default_value=0.0; L(mp.outputs['Vector'],wv.inputs['Vector'])
    cr=nn('ShaderNodeValToRGB','QQR_lapramp'); cr.color_ramp.elements[0].position=0.0; cr.color_ramp.elements[0].color=(0.24,0.235,0.225,1)
    cr.color_ramp.elements[1].position=0.04; cr.color_ramp.elements[1].color=(0.40,0.395,0.38,1); L(wv.outputs['Fac'],cr.inputs['Fac'])
    nz=nn('ShaderNodeTexNoise','QQR_stain'); nz.inputs['Scale'].default_value=0.12; nz.inputs['Detail'].default_value=6; L(tc.outputs['Object'],nz.inputs['Vector'])
    sr=nn('ShaderNodeValToRGB','QQR_stainramp'); sr.color_ramp.elements[0].position=0.45; sr.color_ramp.elements[0].color=(0.62,0.60,0.56,1)
    sr.color_ramp.elements[1].position=0.62; sr.color_ramp.elements[1].color=(1,1,1,1); L(nz.outputs['Fac'],sr.inputs['Fac'])
    mx=nn('ShaderNodeMix','QQR_mul'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
    L(cr.outputs['Color'],mx.inputs['A']); L(sr.outputs['Color'],mx.inputs['B']); L(mx.outputs['Result'],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=0.9
    print('QQR applied')
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QQSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('QQSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QQSAVEAS'],copy=True); print('SAVED_AS')

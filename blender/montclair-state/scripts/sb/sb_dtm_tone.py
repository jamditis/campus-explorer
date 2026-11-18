# sb: Ground_ortho_grass (LiDAR DTM drape) south-west of the Annex reads blue/patchy (baked shade in the 2020 ortho) at eye level.
# Local world-box tone mask (x -185..-95, y 195..252, 6 m fade) pulls the base colour toward the grass texture (qo method).
# Shader-only, UNVERIFIED. REVERT=1 removes SB_ nodes and restores the previous Base Color link (material props sb_prev_*).
import bpy,os
m=bpy.data.materials['Ground_ortho_grass']; nt=m.node_tree; N=nt.nodes; L=nt.links
pb=N['Principled BSDF']; ortho=N['Image Texture.003']; grass=N['Image Texture']
if 'sb_prev_node' in m:
    L.new(N[m['sb_prev_node']].outputs[m['sb_prev_out']],pb.inputs['Base Color']); del m['sb_prev_node']; del m['sb_prev_out']
for n in [n for n in N if n.name.startswith('SB_')]: N.remove(n)
print('SBT reverted')
if os.environ.get('REVERT')!='1':
    s=pb.inputs['Base Color'].links[0].from_socket; m['sb_prev_node']=s.node.name; m['sb_prev_out']=list(s.node.outputs).index(s)
    def nd(t,nm):
        n=N.new(t); n.name=n.label='SB_'+nm; return n
    geo=nd('ShaderNodeNewGeometry','geo'); sep=nd('ShaderNodeSeparateXYZ','sep'); L.new(geo.outputs['Position'],sep.inputs[0])
    F=6.0
    def mr(v,a,b,nm):
        n=nd('ShaderNodeMapRange',nm); n.interpolation_type='SMOOTHSTEP'; n.inputs['From Min'].default_value=a; n.inputs['From Max'].default_value=b; L.new(v,n.inputs['Value']); return n.outputs[0]
    def mul(a,b,nm):
        n=nd('ShaderNodeMath',nm); n.operation='MULTIPLY'
        for i,v in enumerate((a,b)):
            if isinstance(v,float): n.inputs[i].default_value=v
            else: L.new(v,n.inputs[i])
        return n.outputs[0]
    X0,X1,Y0,Y1=-185.,-95.,195.,252.
    box=mul(mul(mr(sep.outputs['X'],X0,X0+F,'x0'),mr(sep.outputs['X'],X1,X1-F,'x1'),'bx'),mul(mr(sep.outputs['Y'],Y0,Y0+F,'y0'),mr(sep.outputs['Y'],Y1,Y1-F,'y1'),'by'),'box')
    fac=mul(box,float(os.environ.get('STR','0.85')),'fac')
    hsv=nd('ShaderNodeHueSaturation','hsv'); L.new(grass.outputs['Color'],hsv.inputs['Color'])
    hsv.inputs['Hue'].default_value=0.5; hsv.inputs['Saturation'].default_value=0.9; hsv.inputs['Value'].default_value=0.80
    tint=nd('ShaderNodeMix','ortho_green'); tint.data_type='RGBA'; tint.blend_type='MULTIPLY'; tint.inputs[0].default_value=1.0
    L.new(ortho.outputs['Color'],tint.inputs[6]); tint.inputs[7].default_value=(0.55,0.68,0.42,1)
    lawn=nd('ShaderNodeMix','lawn'); lawn.data_type='RGBA'; lawn.inputs[0].default_value=0.25
    L.new(hsv.outputs[0],lawn.inputs[6]); L.new(tint.outputs[2],lawn.inputs[7])
    out=nd('ShaderNodeMix','tone_mix'); out.data_type='RGBA'
    L.new(fac,out.inputs[0]); L.new(s,out.inputs[6]); L.new(lawn.outputs[2],out.inputs[7]); L.new(out.outputs[2],pb.inputs['Base Color'])
    print('SBT added',len([n for n in N if n.name.startswith('SB_')]),'prev',m['sb_prev_node'])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

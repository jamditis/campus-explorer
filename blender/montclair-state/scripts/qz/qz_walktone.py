# qz: walks (OV/QT concrete) read near-white next to the qy-toned plaza. Soft world-box gated darkening
# (x -75..195, y 205..365, 15 m fade) inserted before Base Color in OV_Paving_concrete_walk_tone_UNVERIFIED
# and QT_walk_concrete_joints_UNVERIFIED, so walks round Richardson/Student Center plaza match the plaza without
# a seam into the rest of campus. Nodes prefixed QZ_. REVERT=1 removes them and restores the original link.
import bpy,os
MATS=['OV_Paving_concrete_walk_tone_UNVERIFIED','QT_walk_concrete_joints_UNVERIFIED']
X0,X1,Y0,Y1,F=-75.0,195.0,205.0,365.0,15.0
MUL=float(os.environ.get('QZ_MUL','0.70'))
for mn in MATS:
    m=bpy.data.materials[mn]; nt=m.node_tree; N=nt.nodes; L=nt.links
    bs=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]; inp=bs.inputs['Base Color']
    old=[n for n in N if n.name.startswith('QZ_')]
    if old:
        mix=N['QZ_mix']; src=mix.inputs[6].links[0].from_socket if mix.inputs[6].is_linked else None
        for n in old: N.remove(n)
        if src: L.new(src,inp)
    if os.environ.get('REVERT')=='1': print('QZW reverted',mn); continue
    src=inp.links[0].from_socket
    g=N.new('ShaderNodeNewGeometry'); g.name='QZ_geo'
    s=N.new('ShaderNodeSeparateXYZ'); s.name='QZ_sep'; L.new(g.outputs['Position'],s.inputs[0])
    def mr(name,sock,a,b):
        r=N.new('ShaderNodeMapRange'); r.name=name; r.interpolation_type='SMOOTHSTEP'; r.clamp=True
        r.inputs['From Min'].default_value=a; r.inputs['From Max'].default_value=b
        L.new(sock,r.inputs['Value']); return r.outputs['Result']
    gx0=mr('QZ_x0',s.outputs['X'],X0,X0+F); gx1=mr('QZ_x1',s.outputs['X'],X1,X1-F)
    gy0=mr('QZ_y0',s.outputs['Y'],Y0,Y0+F); gy1=mr('QZ_y1',s.outputs['Y'],Y1,Y1-F)
    def mn2(name,a,b):
        n=N.new('ShaderNodeMath'); n.name=name; n.operation='MINIMUM'; L.new(a,n.inputs[0]); L.new(b,n.inputs[1]); return n.outputs[0]
    gate=mn2('QZ_gate',mn2('QZ_gx',gx0,gx1),mn2('QZ_gy',gy0,gy1))
    mix=N.new('ShaderNodeMix'); mix.name='QZ_mix'; mix.data_type='RGBA'; mix.blend_type='MULTIPLY'
    L.new(gate,mix.inputs[0]); L.new(src,mix.inputs[6]); mix.inputs[7].default_value=(MUL,MUL*0.985,MUL*0.96,1)
    L.new(mix.outputs[2],inp)
    print('QZW applied',mn,MUL)
if os.environ.get('QZSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

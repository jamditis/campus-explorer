# qu (3): soil-stained side lips on the older Footpaths_OSM walk slabs round Richardson (qt Next). Shader-only edit of
# OV_Paving_concrete_walk_tone_UNVERIFIED (only user Footpaths_OSM): side faces (|normal.z| < ~0.5) get a damp soil tone,
# gated to the world box x 30-145, y 218-325 with a 6 m fade (same box as qr/qs). UNVERIFIED visual approximation.
# REVERT=1 removes the QU_ nodes and restores the original Base Color link (material prop qu_prev_bc).
import bpy,os
m=bpy.data.materials['OV_Paving_concrete_walk_tone_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
P=N['Principled BSDF']
def revert():
    if 'qu_prev_bc_node' in m:
        L.new(N[m['qu_prev_bc_node']].outputs[m['qu_prev_bc_out']],P.inputs['Base Color']); del m['qu_prev_bc_node']; del m['qu_prev_bc_out']
    for n in [n for n in N if n.name.startswith('QU_')]: N.remove(n)
    print('QUS reverted')
revert()
if os.environ.get('REVERT')=='1':
    if os.environ.get('QUSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
src=P.inputs['Base Color'].links[0].from_socket; m['qu_prev_bc_node']=src.node.name; m['qu_prev_bc_out']=list(src.node.outputs).index(src)
def MN(op,a,b=None,nm='m'):
    n=N.new('ShaderNodeMath'); n.operation=op; n.name='QU_'+nm
    for i,v in enumerate((a,b)):
        if v is None: continue
        if isinstance(v,(int,float)): n.inputs[i].default_value=v
        else: L.new(v,n.inputs[i])
    return n.outputs[0]
def MR(v,a,b,nm):
    n=N.new('ShaderNodeMapRange'); n.name='QU_'+nm; n.interpolation_type='SMOOTHSTEP'; L.new(v,n.inputs[0]); n.inputs[1].default_value=a; n.inputs[2].default_value=b; return n.outputs[0]
g=N.new('ShaderNodeNewGeometry'); g.name='QU_geo'; s=N.new('ShaderNodeSeparateXYZ'); s.name='QU_nsep'; L.new(g.outputs['Normal'],s.inputs[0])
side=MR(MN('ABSOLUTE',s.outputs['Z'],nm='nabs'),0.75,0.35,'side')     # 1 on vertical faces
ps=N.new('ShaderNodeSeparateXYZ'); ps.name='QU_psep'; L.new(g.outputs['Position'],ps.inputs[0])
bx=MN('MULTIPLY',MR(ps.outputs['X'],24,30,'x0'),MR(ps.outputs['X'],151,145,'x1'),'bx')
by=MN('MULTIPLY',MR(ps.outputs['Y'],212,218,'y0'),MR(ps.outputs['Y'],331,325,'y1'),'by')
gate=MN('MULTIPLY',MN('MULTIPLY',bx,by,'box'),side,'gate')
tc=N.new('ShaderNodeTexNoise'); tc.name='QU_noise'; tc.inputs['Scale'].default_value=3.0; tc.inputs['Detail'].default_value=5
L.new(g.outputs['Position'],tc.inputs['Vector'])
amt=MN('MULTIPLY',gate,MN('ADD',MN('MULTIPLY',tc.outputs['Fac'],0.5,'nzm'),0.55,'nz'),'amt')
mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.name='QU_side_mix'; mx.clamp_factor=True
L.new(amt,mx.inputs[0]); L.new(src,mx.inputs[6]); mx.inputs[7].default_value=(0.13,0.105,0.075,1); L.new(mx.outputs[2],P.inputs['Base Color'])
print('QUS side soil nodes added; prev',m['qu_prev_bc_node'],m['qu_prev_bc_out'])
if os.environ.get('QUSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

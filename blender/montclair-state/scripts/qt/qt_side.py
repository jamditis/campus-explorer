# qt (3): side faces of the QS walk ribbons (the 0.3 m skirts) get soil-stained concrete instead of clean grey with
# joint stripes. Edits only QT_walk_concrete_joints_UNVERIFIED (qt material); removed with qt_main REVERT.
import bpy
m=bpy.data.materials['QT_walk_concrete_joints_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
if 'QT_side_geo' not in N:
    g=N.new('ShaderNodeNewGeometry'); g.name='QT_side_geo'; s=N.new('ShaderNodeSeparateXYZ'); s.name='QT_side_sep'; L.new(g.outputs['Normal'],s.inputs[0])
    a=N.new('ShaderNodeMath'); a.operation='ABSOLUTE'; a.name='QT_side_abs'; L.new(s.outputs['Z'],a.inputs[0])
    r=N.new('ShaderNodeMapRange'); r.name='QT_side_mask'; r.interpolation_type='SMOOTHSTEP'; L.new(a.outputs[0],r.inputs[0]); r.inputs[1].default_value=0.7; r.inputs[2].default_value=0.3
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.name='QT_side_mix'
    P=N['Principled BSDF']; src=P.inputs['Base Color'].links[0].from_socket
    L.new(src,mx.inputs[6]); mx.inputs[7].default_value=(0.14,0.115,0.085,1)
    f=N.new('ShaderNodeMath'); f.operation='MULTIPLY'; f.name='QT_side_amt'; L.new(r.outputs[0],f.inputs[0]); f.inputs[1].default_value=0.8; L.new(f.outputs[0],mx.inputs[0])
    L.new(mx.outputs[2],P.inputs['Base Color'])
    # kill joints on sides: multiply joint by (1-side)
    jm=N['QT_joint_mix']; jl=jm.inputs[0].links[0].from_socket
    inv=N.new('ShaderNodeMath'); inv.operation='SUBTRACT'; inv.name='QT_side_inv'; inv.inputs[0].default_value=1; L.new(r.outputs[0],inv.inputs[1])
    jj=N.new('ShaderNodeMath'); jj.operation='MULTIPLY'; jj.name='QT_side_joint'; L.new(jl,jj.inputs[0]); L.new(inv.outputs[0],jj.inputs[1]); L.new(jj.outputs[0],jm.inputs[0])
    print('QTS side mask added')
import os
if os.environ.get('QTSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

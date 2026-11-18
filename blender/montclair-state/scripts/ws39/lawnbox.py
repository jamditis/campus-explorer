# ws39c: force lawn tone on terrain in the College Ave / Kasser frontage box (kills dark 2020-ortho stripes showing through the grass)
import bpy,os
m=bpy.data.materials['Ground_ortho_grass']; nt=m.node_tree; N=nt.nodes; L=nt.links
if 'WS39_box_mix' not in N:
    bs=N['Principled BSDF']; inl=[l for l in L if l.to_node==bs and l.to_socket.name=='Base Color'][0]; src=inl.from_socket
    print('L39 base colour from',inl.from_node.name,src.name)
    g=N.new('ShaderNodeNewGeometry'); g.name='WS39_geo'; sp=N.new('ShaderNodeSeparateXYZ'); sp.name='WS39_sep'; L.new(g.outputs['Position'],sp.inputs[0])
    def ramp(sock,a,b,name):
        r=N.new('ShaderNodeMapRange'); r.name=name; r.clamp=True; L.new(sock,r.inputs['Value'])
        r.inputs['From Min'].default_value=a; r.inputs['From Max'].default_value=b; r.inputs['To Min'].default_value=0; r.inputs['To Max'].default_value=1; return r.outputs['Result']
    def mul(a,b,name):
        x=N.new('ShaderNodeMath'); x.operation='MULTIPLY'; x.name=name; L.new(a,x.inputs[0]); L.new(b,x.inputs[1]); return x.outputs[0]
    X0,X1,Y0,Y1,E=-234.0,-196.0,-142.0,-60.0,1.5
    fx=mul(ramp(sp.outputs['X'],X0,X0+E,'WS39_x0'),ramp(sp.outputs['X'],X1,X1-E,'WS39_x1'),'WS39_bx')
    fy=mul(ramp(sp.outputs['Y'],Y0,Y0+E,'WS39_y0'),ramp(sp.outputs['Y'],Y1,Y1-E,'WS39_y1'),'WS39_by')
    f=mul(fx,fy,'WS39_box')
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.name='WS39_box_mix'
    L.new(f,mx.inputs['Factor']); L.new(src,mx.inputs[6]); L.new(N['Hue/Saturation/Value'].outputs['Color'],mx.inputs[7])
    L.new(mx.outputs[2],bs.inputs['Base Color'])
    print('L39 lawn box inserted',X0,X1,Y0,Y1)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('L39 SAVED')

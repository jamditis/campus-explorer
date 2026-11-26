# ws250 pass 6 (CHAIN on ws250e): the re-snapped subdivided fan faces are long skinny quads (level 4 of 20-40 m fan edges), and
# their twisted children render as thin creases every ~2.5 m (camera-ray probe rl250: normal z 0.4-0.8 bands). Blur the
# subdivided piece's Z (Blur Attribute, 12 iterations, mesh neighbours) with the piece's outline held (weight 0 on boundary
# vertices) so the creases relax onto the smooth LiDAR shape; X/Y untouched.
import bpy
TAG='F250F'; ng=bpy.data.node_groups['WS250_W63_LiDAR_terrain_snap']; N=ng.nodes; L=ng.links
if 'WS250_blur_z' not in N:
    sets=[n for n in N if n.type=='SET_POSITION']; st2=next(s for s in sets if s.inputs['Geometry'].links and s.inputs['Geometry'].links[0].from_node.name=='WS250_subdiv')
    jn=next(n for n in N if n.type=='JOIN_GEOMETRY')
    nt=next(n for n in N if n.type=='BOOLEAN_MATH' and n.operation=='NOT')
    sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; sw.inputs['False'].default_value=0.0; sw.inputs['True'].default_value=1.0; L.new(nt.outputs[0],sw.inputs['Switch'])
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    bl=N.new('GeometryNodeBlurAttribute'); bl.name='WS250_blur_z'; bl.data_type='FLOAT'; bl.inputs['Iterations'].default_value=12
    L.new(sp.outputs['Z'],bl.inputs[0]); L.new(sw.outputs[0],bl.inputs['Weight'])
    mx=N.new('ShaderNodeMix'); mx.data_type='FLOAT'; L.new(sw.outputs[0],mx.inputs['Factor']); L.new(sp.outputs['Z'],mx.inputs[2]); L.new(bl.outputs[0],mx.inputs[3])
    cb=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cb.inputs[0]); L.new(sp.outputs['Y'],cb.inputs[1]); L.new(mx.outputs[0],cb.inputs[2])
    st3=N.new('GeometryNodeSetPosition'); L.new(st2.outputs[0],st3.inputs['Geometry']); L.new(cb.outputs[0],st3.inputs['Position'])
    for l in list(jn.inputs[0].links):
        if l.from_node==st2: L.remove(l)
    L.new(st3.outputs[0],jn.inputs[0]); print(TAG,'blur inserted',flush=True)

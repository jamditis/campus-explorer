# qk (Nov 2 2026) CCIS (b) "tapered tower": the east projecting bay (QF skin box t 215.96..222.48, front n -54.62) looked
# tapered because LiDAR roof eave/soffit/fascia faces of 'Center for Computing and Information Science roof (LiDAR)' (a 5.5 -> 3 m
# wedge, sloping soffit faces at n -54.4..-54.5) poke 0.1-0.2 m IN FRONT of the skin front face. Removable GN
# 'QK_CCIS_tower_wedge_trim' deletes the LiDAR roof faces whose centre lies inside/in front of the skin slab of that bay
# (t 215.8..222.7, n -54.95..-53.9, z 141.2..155.0), so the straight-sided QF stucco bay shows. Frame: t=0.4x+0.92y,
# n=0.92x-0.4y (CCIS east face). APPROXIMATE (real bay width/top unknown; QF skin is itself UNVERIFIED). REVERT=1 removes it.
import bpy, os
REV=os.environ.get('REVERT')=='1'
O=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; MN='QK_CCIS_tower_wedge_trim'; GN=MN+'_GN'
m=O.modifiers.get(MN)
if m: O.modifiers.remove(m)
g=bpy.data.node_groups.get(GN)
if g: bpy.data.node_groups.remove(g)
if 'UNVERIFIED_qk' in O: del O['UNVERIFIED_qk']
if REV: print('QK tower reverted')
else:
    import numpy as np
    assert np.allclose(np.array(O.matrix_world),np.eye(4),atol=1e-5), 'non-identity matrix'
    ng=bpy.data.node_groups.new(GN,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0])
    def lin(a,b):
        m1=N.new('ShaderNodeMath'); m1.operation='MULTIPLY'; L(sp.outputs[0],m1.inputs[0]); m1.inputs[1].default_value=a
        m2=N.new('ShaderNodeMath'); m2.operation='MULTIPLY_ADD'; L(sp.outputs[1],m2.inputs[0]); m2.inputs[1].default_value=b; L(m1.outputs[0],m2.inputs[2]); return m2.outputs[0]
    T=lin(0.4,0.92); Nn=lin(0.92,-0.4)
    sel=None
    for s,lo,hi in ((T,215.8,222.7),(Nn,-54.95,-53.9),(sp.outputs[2],141.2,155.0)):
        for op,v in (('GREATER_THAN',lo),('LESS_THAN',hi)):
            c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L(s,c.inputs[0]); c.inputs[1].default_value=v
            if sel is None: sel=c.outputs[0]
            else: a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L(sel,a.inputs[0]); L(c.outputs[0],a.inputs[1]); sel=a.outputs[0]
    dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L(gi.outputs[0],dl.inputs['Geometry']); L(sel,dl.inputs['Selection']); L(dl.outputs[0],go.inputs[0])
    md=O.modifiers.new(MN,'NODES'); md.node_group=ng
    O['UNVERIFIED_qk']='qk: LiDAR roof wedge faces in front of the QF east bay skin deleted (GN QK_CCIS_tower_wedge_trim)'
    dg=bpy.context.evaluated_depsgraph_get(); print('QK tower trim added, faces now',len(O.evaluated_get(dg).data.polygons))

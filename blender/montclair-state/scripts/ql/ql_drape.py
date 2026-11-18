# ql (3): steep LiDAR roof drape faces (|nz|<0.85) standing in front of the N-S cover plane (centre x>29.33, y 201.4-241.4,
# z 141.3-154.8) = the diagonal 'wedge' in the east views -> GN QL_ccis_east_drape_trim on the CCIS LiDAR roof. REVERT=1 removes.
import bpy, os
REV=os.environ.get('REVERT')=='1'
O=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; MN='QL_ccis_east_drape_trim'
m=O.modifiers.get(MN)
if m: O.modifiers.remove(m)
g=bpy.data.node_groups.get(MN+'_GN')
if g: bpy.data.node_groups.remove(g)
if 'UNVERIFIED_ql' in O: del O['UNVERIFIED_ql']
if not REV:
    ng=bpy.data.node_groups.new(MN+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0])
    nr=N.new('GeometryNodeInputNormal'); sn=N.new('ShaderNodeSeparateXYZ'); L(nr.outputs[0],sn.inputs[0])
    ab=N.new('ShaderNodeMath'); ab.operation='ABSOLUTE'; L(sn.outputs[2],ab.inputs[0])
    sel=None
    for s,op,v in ((sp.outputs[0],'GREATER_THAN',29.33),(sp.outputs[1],'GREATER_THAN',201.4),(sp.outputs[1],'LESS_THAN',241.4),(sp.outputs[2],'GREATER_THAN',141.3),(sp.outputs[2],'LESS_THAN',154.8),(ab.outputs[0],'LESS_THAN',0.85)):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L(s,c.inputs[0]); c.inputs[1].default_value=v
        if sel is None: sel=c.outputs[0]
        else: b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L(sel,b.inputs[0]); L(c.outputs[0],b.inputs[1]); sel=b.outputs[0]
    dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L(gi.outputs[0],dl.inputs['Geometry']); L(sel,dl.inputs['Selection']); L(dl.outputs[0],go.inputs[0])
    dg=bpy.context.evaluated_depsgraph_get(); n0=len(O.evaluated_get(dg).data.polygons)
    md=O.modifiers.new(MN,'NODES'); md.node_group=ng
    O['UNVERIFIED_ql']='ql: steep drape faces in front of the CCIS east N-S cover plane deleted (GN QL_ccis_east_drape_trim)'
    dg=bpy.context.evaluated_depsgraph_get(); print('DRAPE faces',n0,'->',len(O.evaluated_get(dg).data.polygons))
# ql (4): the real wedge = OSM wall faces 36/37 of 'Center for Computing and Information Science walls' whose draped top slopes
# from 154.67 down to 141.09 along the rotated low-wing line and crosses 0.5 m in front of the cover plane (y 204.3-207.1).
# GN QL_ccis_wall_top_clamp sets z=141.09 for verts with x 29.1-30.5, y 204.2-207.2, z>141.09 (2 verts), so that wall top
# meets the low-wing roof; the part behind is covered by the QF skin face + QH junction cover.
W=bpy.data.objects['Center for Computing and Information Science walls']; MN2='QL_ccis_wall_top_clamp'
m=W.modifiers.get(MN2)
if m: W.modifiers.remove(m)
g=bpy.data.node_groups.get(MN2+'_GN')
if g: bpy.data.node_groups.remove(g)
if 'UNVERIFIED_ql' in W: del W['UNVERIFIED_ql']
if not REV:
    ng=bpy.data.node_groups.new(MN2+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0])
    sel=None
    for s,op,v in ((sp.outputs[0],'GREATER_THAN',29.1),(sp.outputs[0],'LESS_THAN',30.5),(sp.outputs[1],'GREATER_THAN',204.2),(sp.outputs[1],'LESS_THAN',207.2),(sp.outputs[2],'GREATER_THAN',141.09)):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L(s,c.inputs[0]); c.inputs[1].default_value=v
        if sel is None: sel=c.outputs[0]
        else: b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L(sel,b.inputs[0]); L(c.outputs[0],b.inputs[1]); sel=b.outputs[0]
    cx=N.new('ShaderNodeCombineXYZ'); L(sp.outputs[0],cx.inputs[0]); L(sp.outputs[1],cx.inputs[1]); cx.inputs[2].default_value=141.09
    stp=N.new('GeometryNodeSetPosition'); L(gi.outputs[0],stp.inputs['Geometry']); L(sel,stp.inputs['Selection']); L(cx.outputs[0],stp.inputs['Position']); L(stp.outputs[0],go.inputs[0])
    md=W.modifiers.new(MN2,'NODES'); md.node_group=ng
    W['UNVERIFIED_ql']='ql: 2 wall-top verts clamped to the low-wing roof 141.09 at the CCIS east S junction (GN QL_ccis_wall_top_clamp)'
    print('CLAMP added')

# ws57: add a final "lift above terrain" GN modifier to Footpaths_OSM and Roads_OSM: each vertex z = max(z, terrain_z + CLR). Idempotent.
import bpy,os
CLR=float(os.environ.get('CLR','0.03'))
NG='WS57_LiftAboveTerrain'
g=bpy.data.node_groups.get(NG)
if g is None:
    g=bpy.data.node_groups.new(NG,'GeometryNodeTree')
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=g.nodes; L=g.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=bpy.data.objects['Terrain_LiDAR_DTM_1m']
    pos=N.new('GeometryNodeInputPosition')
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,50)
    rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=200
    sh=N.new('ShaderNodeSeparateXYZ'); sp=N.new('ShaderNodeSeparateXYZ')
    a=N.new('ShaderNodeMath'); a.operation='ADD'; a.inputs[1].default_value=CLR
    s=N.new('ShaderNodeMath'); s.operation='SUBTRACT'
    m=N.new('ShaderNodeMath'); m.operation='MAXIMUM'; m.inputs[1].default_value=0
    lim=N.new('ShaderNodeMath'); lim.operation='LESS_THAN'; lim.inputs[1].default_value=1.0  # only lift up to 1 m
    k=N.new('ShaderNodeMath'); k.operation='MULTIPLY'
    k2=N.new('ShaderNodeMath'); k2.operation='MULTIPLY'
    cx=N.new('ShaderNodeCombineXYZ')
    sp_=N.new('GeometryNodeSetPosition')
    L.new(gi.outputs[0],sp_.inputs['Geometry']); L.new(sp_.outputs[0],go.inputs[0])
    L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry'])
    L.new(pos.outputs[0],up.inputs[0]); L.new(up.outputs[0],rc.inputs['Source Position'])
    L.new(rc.outputs['Hit Position'],sh.inputs[0]); L.new(pos.outputs[0],sp.inputs[0])
    L.new(sh.outputs['Z'],a.inputs[0]); L.new(a.outputs[0],s.inputs[0]); L.new(sp.outputs['Z'],s.inputs[1])
    L.new(s.outputs[0],m.inputs[0]); L.new(m.outputs[0],lim.inputs[0])
    L.new(m.outputs[0],k.inputs[0]); L.new(lim.outputs[0],k.inputs[1])
    L.new(k.outputs[0],k2.inputs[0]); L.new(rc.outputs['Is Hit'],k2.inputs[1])
    L.new(k2.outputs[0],cx.inputs['Z']); L.new(cx.outputs[0],sp_.inputs['Offset'])
for n in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects.get(n)
    if o and 'WS57_lift' not in o.modifiers:
        md=o.modifiers.new('WS57_lift','NODES'); md.node_group=g
    print('L57 mods',n,[x.name for x in o.modifiers][-4:])
bpy.context.view_layer.update()

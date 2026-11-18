# ws57b: inside BOX only: separate pavement faces, subdivide (simple, level 2), lift each vertex to max(z, terrain_z+CLR) (cap 0.4 m), rejoin.
import bpy,os
CLR=0.03
BOXES={'Footpaths_OSM':((53,-87),(63,-76)),'Roads_OSM':((101,-12),(106,-8))}
def build(name,lo,hi):
    g=bpy.data.node_groups.new(name,'GeometryNodeTree')
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=g.nodes; L=g.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    def cmp(sock,val,op):
        c=N.new('ShaderNodeMath'); c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
    def band(a,b):
        c=N.new('FunctionNodeBooleanMath'); c.operation='AND'; L.new(a,c.inputs[0]); L.new(b,c.inputs[1]); return c.outputs[0]
    sel=band(band(cmp(sp.outputs['X'],lo[0],'GREATER_THAN'),cmp(sp.outputs['X'],hi[0],'LESS_THAN')),band(cmp(sp.outputs['Y'],lo[1],'GREATER_THAN'),cmp(sp.outputs['Y'],hi[1],'LESS_THAN')))
    sg=N.new('GeometryNodeSeparateGeometry'); sg.domain='FACE'
    L.new(gi.outputs[0],sg.inputs['Geometry']); L.new(sel,sg.inputs['Selection'])
    sd=N.new('GeometryNodeSubdivideMesh'); sd.inputs['Level'].default_value=2; L.new(sg.outputs['Selection'],sd.inputs['Mesh'])
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=bpy.data.objects['Terrain_LiDAR_DTM_1m']
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,50); L.new(pos.outputs[0],up.inputs[0])
    rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=200
    L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
    sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
    d=N.new('ShaderNodeMath'); d.operation='SUBTRACT'; L.new(cmp(sh.outputs['Z'],CLR,'ADD'),d.inputs[0]); L.new(sp.outputs['Z'],d.inputs[1])
    m=N.new('ShaderNodeMath'); m.operation='MAXIMUM'; m.inputs[1].default_value=0; L.new(d.outputs[0],m.inputs[0])
    mn=cmp(m.outputs[0],0.4,'MINIMUM')
    k=N.new('ShaderNodeMath'); k.operation='MULTIPLY'; L.new(mn,k.inputs[0]); L.new(rc.outputs['Is Hit'],k.inputs[1])
    cx=N.new('ShaderNodeCombineXYZ'); L.new(k.outputs[0],cx.inputs['Z'])
    st=N.new('GeometryNodeSetPosition'); L.new(sd.outputs[0],st.inputs['Geometry']); L.new(cx.outputs[0],st.inputs['Offset'])
    j=N.new('GeometryNodeJoinGeometry'); L.new(sg.outputs['Inverted'],j.inputs[0]); L.new(st.outputs[0],j.inputs[0])
    L.new(j.outputs[0],go.inputs[0]); return g
for n,(lo,hi) in BOXES.items():
    o=bpy.data.objects.get(n)
    if o and 'WS57_local_lift' not in o.modifiers:
        md=o.modifiers.new('WS57_local_lift','NODES'); md.node_group=build('WS57_local_lift_'+n,lo,hi)
bpy.context.view_layer.update(); print('L57 lift2 added')

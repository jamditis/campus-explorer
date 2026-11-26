# ws248 W62g: the ground E of the soccer field's east stand (x -246..-186, y 40..140) came from PB_terrain_fan_regrid's
# linear fan across the old no-data hole: a tilted plane 1.0 m too LOW at the S end and up to 2.2 m too HIGH at the N end
# vs LiDAR class-2 ground (2023 J5D6, 2017 fallback; both agree: flat ~134.3-134.5 behind the stand). That plane made the
# 'bank' N of the stand and tilted the ws247 back walk. Fix: GN snap of the evaluated terrain to a 1 m LiDAR target
# (3x3 mean, nan-median fill), weight 'w248' = 1 inside, 3-6 m feathers; inserted BEFORE the WS243 hold-under so the
# stands/pitch hold-under (lower-only) still applies on top.
import bpy, json
TAG='F248B'; TN='WS248_E_stand_LiDAR2023_ground_target'; MN='WS248_E_stand_LiDAR_terrain_snap'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
if TN not in bpy.data.objects:
    J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws248/t248.json'))
    me=bpy.data.meshes.new(TN); me.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); me.update()
    a=me.attributes.new('w248','FLOAT','POINT'); a.data.foreach_set('value',J['W'])
    o=bpy.data.objects.new(TN,me); o.hide_render=True; o.display_type='WIRE'
    ref=bpy.data.objects.get('WS245_E_bank_grade_target_UNVERIFIED')
    cols=ref.users_collection if ref else T.users_collection
    for c in cols: c.objects.link(o)
    print(TAG,'target',TN,len(me.vertices),len(me.polygons),[c.name for c in cols],flush=True)
tgt=bpy.data.objects[TN]
if MN not in T.modifiers:
    ng=bpy.data.node_groups.new(MN,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=tgt; oi.transform_space='RELATIVE'
    pos=N.new('GeometryNodeInputPosition')
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L.new(pos.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,300)
    rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'
    na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='w248'
    L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(na.outputs['Attribute'],rc.inputs['Attribute'])
    L.new(up.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=600
    sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
    wm=N.new('ShaderNodeMath'); wm.operation='MULTIPLY'; L.new(rc.outputs['Attribute'],wm.inputs[0]); L.new(rc.outputs['Is Hit'],wm.inputs[1])
    cl=N.new('ShaderNodeClamp'); L.new(wm.outputs[0],cl.inputs[0])
    mx=N.new('ShaderNodeMix'); mx.data_type='FLOAT'; L.new(cl.outputs[0],mx.inputs['Factor']); L.new(sp.outputs['Z'],mx.inputs[2]); L.new(sh.outputs['Z'],mx.inputs[3])
    cb=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cb.inputs[0]); L.new(sp.outputs['Y'],cb.inputs[1]); L.new(mx.outputs[0],cb.inputs[2])
    st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(cb.outputs[0],st.inputs['Position']); L.new(st.outputs[0],go.inputs[0])
    m=T.modifiers.new(MN,'NODES'); m.node_group=ng
    names=[x.name for x in T.modifiers]; tgt_i=names.index('WS243_terrain_hold_under_stands_pitch')
    with bpy.context.temp_override(object=T): bpy.ops.object.modifier_move_to_index(modifier=MN,index=tgt_i)
    print(TAG,'modifier stack',[x.name for x in T.modifiers][-5:],flush=True)

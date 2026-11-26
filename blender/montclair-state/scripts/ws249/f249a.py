# ws249 (CHAIN via ws208/merge208.py): two LiDAR snap targets + raycast-snap GN modifiers (same design as ws248 f248b):
#  (1) WS249_W_slope_LiDAR2023_ground_target  -> GN WS249_W_slope_LiDAR_terrain_snap on PK_Feliciano_west_DTM_fill_UNVERIFIED
#      (index 0, before WS243 hold-under). The fill put the soccer field's W embankment (133.6 -> 121 m) ~5 m off: up to
#      3 m too low at the top, 2-3 m too high at the foot vs 2023 J5D5 LiDAR (2017 agrees to ~0.15 m).
#  (2) WS249_SE_berm_LiDAR2023_ground_target -> GN WS249_SE_berm_LiDAR_terrain_snap on Terrain_LiDAR_DTM_1m, right after
#      WS248_E_stand_LiDAR_terrain_snap (ws248 residual: feather up to 0.9 m off on the berm SE of the east stand).
import bpy, json
TAG='F249A'; J='/workspace/nj-scenes/montclair-state/scripts/ws249/'
def target(name,js,ref):
    if name in bpy.data.objects: return bpy.data.objects[name]
    D=json.load(open(J+js)); me=bpy.data.meshes.new(name); me.from_pydata(D['V'],[],[tuple(f) for f in D['F']]); me.update()
    a=me.attributes.new('w249','FLOAT','POINT'); a.data.foreach_set('value',D['W'])
    o=bpy.data.objects.new(name,me); o.hide_render=True; o.hide_viewport=False; o.display_type='WIRE'
    for c in ref.users_collection: c.objects.link(o)
    print(TAG,'target',name,len(me.vertices),[c.name for c in ref.users_collection],flush=True); return o
def snap(obj,mn,tgt,after=None,before=None):
    if mn in obj.modifiers: return
    ng=bpy.data.node_groups.new(mn,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=tgt; oi.transform_space='RELATIVE'
    pos=N.new('GeometryNodeInputPosition')
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L.new(pos.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,300)
    rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'
    na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='w249'
    L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(na.outputs['Attribute'],rc.inputs['Attribute'])
    L.new(up.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=600
    sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0]); sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
    wm=N.new('ShaderNodeMath'); wm.operation='MULTIPLY'; L.new(rc.outputs['Attribute'],wm.inputs[0]); L.new(rc.outputs['Is Hit'],wm.inputs[1])
    cl=N.new('ShaderNodeClamp'); L.new(wm.outputs[0],cl.inputs[0])
    mx=N.new('ShaderNodeMix'); mx.data_type='FLOAT'; L.new(cl.outputs[0],mx.inputs['Factor']); L.new(sp.outputs['Z'],mx.inputs[2]); L.new(sh.outputs['Z'],mx.inputs[3])
    cb=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cb.inputs[0]); L.new(sp.outputs['Y'],cb.inputs[1]); L.new(mx.outputs[0],cb.inputs[2])
    st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(cb.outputs[0],st.inputs['Position']); L.new(st.outputs[0],go.inputs[0])
    m=obj.modifiers.new(mn,'NODES'); m.node_group=ng
    names=[x.name for x in obj.modifiers]
    idx=names.index(after)+1 if after else (names.index(before) if before else 0)
    with bpy.context.temp_override(object=obj): bpy.ops.object.modifier_move_to_index(modifier=mn,index=idx)
    print(TAG,obj.name,'stack',[x.name for x in obj.modifiers],flush=True)
PK=bpy.data.objects['PK_Feliciano_west_DTM_fill_UNVERIFIED']; T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
ref=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_target']
tw=target('WS249_W_slope_LiDAR2023_ground_target','t249w.json',ref)
ts=target('WS249_SE_berm_LiDAR2023_ground_target','t249se.json',ref)
snap(PK,'WS249_W_slope_LiDAR_terrain_snap',tw,before='WS243_terrain_hold_under_stands_pitch')
snap(T,'WS249_SE_berm_LiDAR_terrain_snap',ts,after='WS248_E_stand_LiDAR_terrain_snap')
# the hidden ws248 target is not in render; keep ours the same way
for o in (tw,ts): o.hide_render=True

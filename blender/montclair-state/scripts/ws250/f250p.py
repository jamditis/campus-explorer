# ws250 (CHAIN via ws208/merge208.py on main ws249f): UNIFY W63 — raise-only 1 m LiDAR ground patch (h250.json) for the lawn
# N of Dickson Hall / E of Feliciano, JOINED into Terrain_LiDAR_DTM_1m by GN WS250_W63_LiDAR_patch_join_terrain (right after
# WS249_SE_berm_LiDAR_terrain_snap), so Footpaths_OSM's OO_redrape (raycast to the evaluated terrain) lands on the raised ground.
# The patch object itself is hidden from render (geometry comes through the join). University Hall is not touched (not in main).
import bpy, json
TAG='F250P'; PN='WS250_W63_lawn_LiDAR2023_ground_patch_1m'; MN='WS250_W63_LiDAR_patch_join_terrain'
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws250/h250.json'))
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; ref=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_target']
if PN not in bpy.data.objects:
    me=bpy.data.meshes.new(PN); me.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); me.validate(); me.update()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(T.data.materials[0])
    uv=me.uv_layers.new(name='ortho')
    for p in me.polygons:
        for li in p.loop_indices: uv.data[li].uv=J['UV'][me.loops[li].vertex_index]
    o=bpy.data.objects.new(PN,me); o.hide_render=True; o.display_type='WIRE'
    for c in ref.users_collection: c.objects.link(o)
    print(TAG,'patch',PN,len(me.vertices),len(me.polygons),me.materials[0].name,[c.name for c in o.users_collection],flush=True)
P=bpy.data.objects[PN]
if MN not in T.modifiers:
    ng=bpy.data.node_groups.new(MN,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=P; oi.transform_space='RELATIVE'
    jn=N.new('GeometryNodeJoinGeometry'); L.new(oi.outputs['Geometry'],jn.inputs[0]); L.new(gi.outputs[0],jn.inputs[0]); L.new(jn.outputs[0],go.inputs[0])
    m=T.modifiers.new(MN,'NODES'); m.node_group=ng
    names=[x.name for x in T.modifiers]; idx=names.index('WS249_SE_berm_LiDAR_terrain_snap')+1
    with bpy.context.temp_override(object=T): bpy.ops.object.modifier_move_to_index(modifier=MN,index=idx)
    print(TAG,'stack',[x.name for x in T.modifiers],flush=True)

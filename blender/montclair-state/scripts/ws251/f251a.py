# ws251 (CHAIN via ws208/merge208.py on main ws250q): UNIFY W63b — lower the Feliciano/Dickson passage to the 2023 LiDAR.
# (1) Terrain_LiDAR_DTM_1m BASE mesh: bmesh bisect along the box lines x -195/-163, y 139/179 (only faces overlapping the box;
#     the big PB fan faces are planar so the cuts add no creases), then delete the faces wholly inside the box -> a clean
#     rectangular hole; (2) drop the ws250 W63 raise-only patch quads inside the box; (3) add h251.json (full LiDAR patch,
#     feathered 3 m to the old surface at the box edge, 0.3 m skirts) hidden, JOINED into the terrain by GN
#     WS251_W63b_passage_LiDAR_patch_join_terrain (name matches subrend TRX) right after WS250_W63_LiDAR_patch_join_terrain (Footpaths_OSM redrape follows).
import bpy, bmesh, json
from mathutils import Vector
TAG='F251A'; PN='WS251_W63b_passage_LiDAR2023_ground_patch_1m'; MN='WS251_W63b_passage_LiDAR_patch_join_terrain'
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws251/h251.json')); x0,x1,y0,y1=J['box']; e=1e-3
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; P3=bpy.data.objects['WS250_W63_lawn_LiDAR2023_ground_patch_1m']
Mi=T.matrix_world.inverted(); M=T.matrix_world
print(TAG,'T matrix',[list(r) for r in M],flush=True)
if PN not in bpy.data.objects:
    bm=bmesh.new(); bm.from_mesh(T.data); nf0=len(bm.faces)
    def over(f):
        ws=[M@v.co for v in f.verts]; return not (max(w.x for w in ws)<x0-e or min(w.x for w in ws)>x1+e or max(w.y for w in ws)<y0-e or min(w.y for w in ws)>y1+e)
    for co,no in (((x0,0,0),(1,0,0)),((x1,0,0),(1,0,0)),((0,y0,0),(0,1,0)),((0,y1,0),(0,1,0))):
        fs=[f for f in bm.faces if over(f)]
        es=list({ed for f in fs for ed in f.edges}); vv=list({v for f in fs for v in f.verts})
        pc=Mi@Vector(co); pn=(Mi.to_3x3().inverted().transposed()@Vector(no)).normalized()
        bmesh.ops.bisect_plane(bm,geom=fs+es+vv,dist=1e-4,plane_co=pc,plane_no=pn)
    dl=[f for f in bm.faces if all(x0-e<=(M@v.co).x<=x1+e and y0-e<=(M@v.co).y<=y1+e for v in f.verts)]
    ar=sum(f.calc_area() for f in dl)
    bmesh.ops.delete(bm,geom=dl,context='FACES_ONLY')
    print(TAG,'terrain faces',nf0,'->',len(bm.faces),'deleted',len(dl),'area %.0f m2 (box %.0f)'%(ar,(x1-x0)*(y1-y0)),flush=True)
    bm.to_mesh(T.data); bm.free(); T.data.update()
    bm=bmesh.new(); bm.from_mesh(P3.data); M3=P3.matrix_world
    d3=[f for f in bm.faces if x0<(M3@f.calc_center_median()).x<x1 and y0<(M3@f.calc_center_median()).y<y1]
    bmesh.ops.delete(bm,geom=d3,context='FACES_ONLY'); print(TAG,'W63 patch quads dropped in box',len(d3),flush=True)
    bm.to_mesh(P3.data); bm.free(); P3.data.update()
    me=bpy.data.meshes.new(PN); me.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); me.validate(); me.update()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(T.data.materials[0])
    uv=me.uv_layers.new(name='ortho')
    for p in me.polygons:
        for li in p.loop_indices: uv.data[li].uv=J['UV'][me.loops[li].vertex_index]
    o=bpy.data.objects.new(PN,me); o.hide_render=True; o.display_type='WIRE'
    for c in P3.users_collection: c.objects.link(o)
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
    names=[x.name for x in T.modifiers]; idx=names.index('WS250_W63_LiDAR_patch_join_terrain')+1
    with bpy.context.temp_override(object=T): bpy.ops.object.modifier_move_to_index(modifier=MN,index=idx)
    print(TAG,'stack',[x.name for x in T.modifiers],flush=True)

# ws243 slice-5 seat fix (probe243a on ws243a). Stands/pitch NOT moved (flat built pitch at 133.6, north-file design).
#  (1) ground poking through turf / pads / walkways / fence feet (Terrain_LiDAR_DTM_1m up to 1.9 m on the east bank): one
#      hidden hold-under target (copies of the stand/pitch base surfaces) + a GN modifier at the END of each ground stack that
#      holds every evaluated ground point 0.06 m under the target (never raises; WS241 pattern).
#  (2) where the ground falls away under the pitch / east stand pad / walkways (up to 9 m at the S end over the WS60 feather,
#      1.7 m under the east pad): a vertical concrete edge wall from every boundary edge down D m (buried where ground is
#      higher). Built platform edge = UNVERIFIED (no photo of the S end).
#  (3) SF north cap walk + curb (buried 0.1-3.3 m under main's ground): appended and RAISED per vertex to evaluated ground + 0.03.
import bpy, bmesh, json, ctypes
from mathutils import Vector
MS='/workspace/nj-scenes/montclair-state/'
TG=['fs_turf','fr_stand_under_pad','fse_stand_under_pad','fr_front_walkway','fse_front_walkway','fst_front_walkway','fr_stand_entry_steps','fse_stand_entry_steps','fst_stand_entry_steps']
bm=bmesh.new()
for n in TG:
    o=bpy.data.objects[n]; t=bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
    me=bpy.data.meshes.new('tmp243'); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
tme=bpy.data.meshes.new('WS243_stands_pitch_holdunder_target'); bm.to_mesh(tme); bm.free()
tgt=bpy.data.objects.new('WS243_stands_pitch_holdunder_target',tme); tgt.hide_render=True; tgt.display_type='WIRE'
NM=bpy.data.collections['NORTH_MERGE']; NM.objects.link(tgt)
def hold(obj,target,off):
    ng=bpy.data.node_groups.new('WS243_under_stands_pitch','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=target
    pos=N.new('GeometryNodeInputPosition'); up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,30); L.new(pos.outputs[0],up.inputs[0])
    rc=N.new('GeometryNodeRaycast'); L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
    rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=60
    sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0]); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; tz.inputs[1].default_value=off; L.new(sh.outputs['Z'],tz.inputs[0])
    cmp=N.new('ShaderNodeMath'); cmp.operation='GREATER_THAN'; L.new(sp.outputs['Z'],cmp.inputs[0]); L.new(tz.outputs[0],cmp.inputs[1])
    # only points within 3 m under the target (deep ground under raked seating is left alone)
    dz=N.new('ShaderNodeMath'); dz.operation='SUBTRACT'; L.new(tz.outputs[0],dz.inputs[0]); L.new(sp.outputs['Z'],dz.inputs[1])
    near=N.new('ShaderNodeMath'); near.operation='GREATER_THAN'; L.new(dz.outputs[0],near.inputs[0]); near.inputs[1].default_value=-3.0
    a1=N.new('FunctionNodeBooleanMath'); a1.operation='AND'; L.new(rc.outputs['Is Hit'],a1.inputs[0]); L.new(cmp.outputs[0],a1.inputs[1])
    a2=N.new('FunctionNodeBooleanMath'); a2.operation='AND'; L.new(a1.outputs[0],a2.inputs[0]); L.new(near.outputs[0],a2.inputs[1])
    cx=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cx.inputs['X']); L.new(sp.outputs['Y'],cx.inputs['Y']); L.new(tz.outputs[0],cx.inputs['Z'])
    st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(a2.outputs[0],st.inputs['Selection']); L.new(cx.outputs[0],st.inputs['Position'])
    L.new(st.outputs[0],go.inputs[0])
    m=obj.modifiers.new(ng.name,'NODES'); m.node_group=ng; m.show_viewport=False
    v=ctypes.c_int.from_address(m.as_pointer()+20); v.value=v.value|1
GN=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('M3b_','Context_skirt','Terrain_LiDAR_DTM_1m','WS68_RHD_ground','WS60_terrain','PK_','PZ_Feliciano'))]
for g in GN: hold(g,tgt,0.06); print('F243A hold-under on',g.name[:40],flush=True)
mat=next((m for m in bpy.data.materials if 'concrete' in m.name.lower() and 'wall' in m.name.lower()),None) or next((m for m in bpy.data.materials if 'concrete' in m.name.lower()),None)
print('F243A wall material',mat and mat.name,flush=True)
WD={'fs_turf':10.0,'fse_stand_under_pad':3.0,'fr_stand_under_pad':1.0,'fse_front_walkway':2.0,'fr_front_walkway':0.6,'fst_front_walkway':1.0}
for n,D in WD.items():
    o=bpy.data.objects[n]; t=bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
    out=bmesh.new(); k=0
    for e in t.edges:
        if not e.is_boundary: continue
        a,b=e.verts[0].co.copy(),e.verts[1].co.copy()
        vs=[out.verts.new(a-Vector((0,0,0.02))),out.verts.new(b-Vector((0,0,0.02))),out.verts.new(b-Vector((0,0,D))),out.verts.new(a-Vector((0,0,D)))]
        out.faces.new(vs); k+=1
    t.free(); me=bpy.data.meshes.new('WS243_edge_wall_'+n); out.to_mesh(me); out.free()
    if mat: me.materials.append(mat)
    w=bpy.data.objects.new('WS243_edge_wall_'+n+'_UNVERIFIED',me); o.users_collection[0].objects.link(w)
    print('F243A edge wall',n,k,'faces depth',D,flush=True)
T=json.load(open(MS+'scripts/ws243/probe243a_targets.json'))
X=[n for n in T if n.startswith('SF north cap')]
with bpy.data.libraries.load(MS+'north/montclair_north.blend',link=False) as (a,b): b.objects=list(X)
sf=bpy.data.collections.get('N_site_detail_sprague_field_apron') or NM
for o in b.objects:
    if o is None: continue
    sf.objects.link(o); M=o.matrix_world; Mi=M.inverted(); d=T[o.name]; k=0; mx=0
    for v,dd in zip(o.data.vertices,d):
        if dd is None or dd<-0.03: continue
        w=M@v.co; w.z+=dd+0.03; v.co=Mi@w; k+=1; mx=max(mx,dd+0.03)
    o.data.update()
    for m in o.modifiers: m.show_viewport=False; _OFF.append((o.name,m.name))
    print('F243A raised',o.name[:40],k,'max',round(mx,2),flush=True)
J={}; J['f243a']={'target':tgt.name,'walls':['WS243_edge_wall_'+n+'_UNVERIFIED' for n in WD],'sf_cap':X}
json.dump(J,open(MS+'scripts/ws243/f243a_out.json','w'),indent=0)

# ws234 M3a step 3: the Context skirt is re-subdivided/re-projected by its GN stack (3.5 M evaluated verts), so base-mesh
# lowering alone left it 0.05-4.8 m ABOVE the M3a extension at 16% of a 5 m grid (probe234f_c). Add one GN modifier at the END
# of the skirt stack: ray-cast each evaluated skirt point straight down onto the extension and, where it hits, hold the skirt
# 0.35 m under the extension (never raises the skirt). Same pattern as the WF/WT/WU skirt_under modifiers.
import bpy
EXT=bpy.data.objects[[n for n in ('M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam','M3a_north_LiDAR_DTM_1m_ext_UNVERIFIED_seam') if n in bpy.data.objects][0]]
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
print('F234G skirt matrix identity',sk.matrix_world==sk.matrix_world.__class__.Identity(4),'ext identity',EXT.matrix_world==EXT.matrix_world.__class__.Identity(4),flush=True)
ng=bpy.data.node_groups.new('WS234_skirt_under_M3a_ext','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=EXT
pos=N.new('GeometryNodeInputPosition')
up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,400)
L.new(pos.outputs[0],up.inputs[0])
rc=N.new('GeometryNodeRaycast')
L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry'])
L.new(up.outputs[0],rc.inputs['Source Position'])
rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=2000
sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; tz.inputs[1].default_value=0.35; L.new(sh.outputs['Z'],tz.inputs[0])
cmp=N.new('ShaderNodeMath'); cmp.operation='GREATER_THAN'; L.new(sp.outputs['Z'],cmp.inputs[0]); L.new(tz.outputs[0],cmp.inputs[1])
an=N.new('FunctionNodeBooleanMath'); an.operation='AND'; L.new(rc.outputs['Is Hit'],an.inputs[0]); L.new(cmp.outputs[0],an.inputs[1])
cx=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cx.inputs['X']); L.new(sp.outputs['Y'],cx.inputs['Y']); L.new(tz.outputs[0],cx.inputs['Z'])
st=N.new('GeometryNodeSetPosition')
L.new(gi.outputs[0],st.inputs['Geometry']); L.new(an.outputs[0],st.inputs['Selection']); L.new(cx.outputs[0],st.inputs['Position'])
L.new(st.outputs[0],go.inputs[0])
m=sk.modifiers.new('WS234_skirt_under_M3a_ext','NODES'); m.node_group=ng
print('F234G modifier added; stack tail',[x.name for x in sk.modifiers][-3:],flush=True)

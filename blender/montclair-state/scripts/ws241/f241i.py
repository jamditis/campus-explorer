# m2c241 follow-up 3 (ws241): the Context skirt is coarse around Lot 28S (x -218..-156), so skirt faces straddling the lot's
# W edge still poke through it (probe241g: 459/24128 faces, <= 0.38 m) even with the ray-cast hold-under (f241g only moves
# skirt POINTS that sit under the lot). Replace the KQ ray-cast modifier with a proximity version: every evaluated skirt point
# within 9 m (3D; skirt faces here are coarse) of the lot surface and higher than (nearest lot point z - 0.10) is held 0.10 m under that z. Never raises.
import bpy, ctypes
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
lot=next(o for o in bpy.data.objects if o.name.startswith('KQ Lot 28S asphalt'))
for m in list(sk.modifiers):
    if m.name.startswith('WS241_skirt_under_KQ'):
        nm=m.name; _OFF[:]=[x for x in _OFF if not (x[0]==sk.name and x[1]==nm)]   # merge208 restore list
        sk.modifiers.remove(m); print('F241I removed',nm,flush=True)
ng=bpy.data.node_groups.new('WS241_skirt_prox_under_Lot28S','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=lot
pos=N.new('GeometryNodeInputPosition')
px=N.new('GeometryNodeProximity'); px.target_element='FACES'
L.new(oi.outputs['Geometry'],px.inputs[0]); L.new(pos.outputs[0],px.inputs['Source Position'])
sh=N.new('ShaderNodeSeparateXYZ'); L.new(px.outputs['Position'],sh.inputs[0])
sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; tz.inputs[1].default_value=0.10; L.new(sh.outputs['Z'],tz.inputs[0])
c1=N.new('ShaderNodeMath'); c1.operation='GREATER_THAN'; L.new(sp.outputs['Z'],c1.inputs[0]); L.new(tz.outputs[0],c1.inputs[1])
c2=N.new('ShaderNodeMath'); c2.operation='LESS_THAN'; L.new(px.outputs['Distance'],c2.inputs[0]); c2.inputs[1].default_value=9.0
an=N.new('ShaderNodeMath'); an.operation='MULTIPLY'; L.new(c1.outputs[0],an.inputs[0]); L.new(c2.outputs[0],an.inputs[1])
cx=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cx.inputs['X']); L.new(sp.outputs['Y'],cx.inputs['Y']); L.new(tz.outputs[0],cx.inputs['Z'])
st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(an.outputs[0],st.inputs['Selection']); L.new(cx.outputs[0],st.inputs['Position'])
L.new(st.outputs[0],go.inputs[0])
m=sk.modifiers.new(ng.name,'NODES'); m.node_group=ng; m.show_viewport=False
v=ctypes.c_int.from_address(m.as_pointer()+20); v.value=v.value|1
print('F241I skirt modifier',m.name,'tail',[x.name for x in sk.modifiers][-4:],flush=True)

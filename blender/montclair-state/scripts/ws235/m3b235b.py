# ws235 M3b step 2: probe235f_a showed the evaluated skirt 0.05-0.63 m ABOVE the corridor patch at 146 of 2183 grid points,
# all along the rail cut/embankment: the skirt's coarse faces bridge the concave cut between clamped verts. Under the patch the
# skirt is never visible, so hold it 1.5 m (not 0.35) under the patch there; the 20 m feather outside keeps edge - 0.35.
import bpy
ng=bpy.data.node_groups['WS235_skirt_under_M3b_corridor_feather']
hit=None
for n in ng.nodes:
    if n.bl_idname=='ShaderNodeMath' and n.operation=='SUBTRACT' and n.inputs[0].is_linked:
        src=n.inputs[0].links[0].from_node
        if src.bl_idname=='ShaderNodeSeparateXYZ' and src.inputs[0].is_linked and src.inputs[0].links[0].from_node.bl_idname=='GeometryNodeRaycast':
            hit=n
assert hit, 'F235B no hit node'
hit.inputs[1].default_value=1.5
print('F235B under-patch margin',hit.inputs[1].default_value,flush=True)

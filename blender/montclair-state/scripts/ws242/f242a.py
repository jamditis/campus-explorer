# ws242 W59: the see-through cracks in Context_skirt W of the police building come from WS237_skirt_under_W53q_lowered_edges
# (probe242a: 0 boundary edges in x -420..-320, y -80..10 before it, 242 after). f237a split the skirt with Separate Geometry
# (faces within 4 m of PK/PZ/WS60/WS68), lowered only the selected part and re-joined it unwelded, so every shared edge
# between a lowered and an unlowered face opened into a crack. Re-wire in place: no split; Set Position on the whole skirt
# with the same selection field (evaluated per vertex) -> neighbours stay connected (the step becomes a short slope).
# The PK north-tip level-2 subdivision box is kept (separated + subdivided as before) and then welded back (merge by distance
# 1 mm, tip box only). Lower-only, as before; no ground or paving moves.
import bpy
ng=bpy.data.node_groups['WS237_skirt_under_W53q_lowered_edges']; N=ng.nodes; L=ng.links.new
sg=[n for n in N if n.bl_idname=='GeometryNodeSeparateGeometry' and n.inputs['Geometry'].links and n.inputs['Geometry'].links[0].from_node.bl_idname=='NodeGroupInput'][0]
st=[n for n in N if n.bl_idname=='GeometryNodeSeparateGeometry' and n.name!=sg.name][0]
sp=[n for n in N if n.bl_idname=='GeometryNodeSetPosition'][0]
go=[n for n in N if n.bl_idname=='NodeGroupOutput'][0]; gi=[n for n in N if n.bl_idname=='NodeGroupInput'][0]
selF=sg.inputs['Selection'].links[0].from_socket
tipsel=st.inputs['Selection'].links[0].from_socket
sd=sp.inputs['Geometry'].links[0].from_node
# tip faces = tip box AND selF (as before: tip separation ran on sg's selected faces)
b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L(tipsel,b.inputs[0]); L(selF,b.inputs[1])
L(gi.outputs[0],st.inputs['Geometry']); L(b.outputs[0],st.inputs['Selection'])
mg=N.new('GeometryNodeMergeByDistance'); mg.inputs['Distance'].default_value=0.001
L(sd.outputs[0],mg.inputs['Geometry']); L(tipsel,mg.inputs['Selection'])
L(mg.outputs[0],sp.inputs['Geometry']); L(selF,sp.inputs['Selection'])
L(sp.outputs[0],go.inputs[0])
N.remove(sg)
print('F242A rewired WS237 skirt group: no split, set-position selection + tip weld',flush=True)

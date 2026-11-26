# ws250 pass 5 (CHAIN on ws250d): the boundary hold (weight x (1 - boundary)) made 0.06 m-wide near-vertical slivers wherever a
# held boundary vertex sat away from the LiDAR (15k steep faces; the dark straight grooves in the eye test). The hold is dropped:
# every subdivided vertex takes the plain feathered target weight. Outline T-junction gaps are bounded by the LiDAR's deviation
# from the straight (already snapped) neighbour edges, which are <= ~2 m long (neighbours are faces <= 1.5 m2).
import bpy
TAG='F250E'; ng=bpy.data.node_groups['WS250_W63_LiDAR_terrain_snap']; N=ng.nodes; L=ng.links
nt=next((n for n in N if n.type=='BOOLEAN_MATH' and n.operation=='NOT'),None)
if nt is not None:
    for l in list(nt.outputs[0].links):
        m=l.to_node; L.remove(l); m.inputs[1].default_value=1.0
    print(TAG,'boundary hold removed',flush=True)

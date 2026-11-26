# ws250 pass 4 (CHAIN on ws250c): the ws250c eye test showed dark straight grooves along the old fan-face edges: the PB fan faces
# are not welded to each other (duplicate verts per face), so every face edge counted as a boundary of the separated piece and
# kept its straight old line while the face interiors snapped. Fix: Merge by Distance (5 mm) on the separated piece BEFORE the
# subdivide, so only the true outline (shared with the untouched neighbours) stays fixed.
import bpy
TAG='F250D'; ng=bpy.data.node_groups['WS250_W63_LiDAR_terrain_snap']; N=ng.nodes; L=ng.links
sd=N['WS250_subdiv']
if 'WS250_weld_before_subdiv' not in N:
    src=sd.inputs['Mesh'].links[0].from_socket
    mg=N.new('GeometryNodeMergeByDistance'); mg.name='WS250_weld_before_subdiv'; mg.inputs['Distance'].default_value=0.005
    L.new(src,mg.inputs['Geometry']); L.new(mg.outputs[0],sd.inputs['Mesh']); print(TAG,'weld inserted',flush=True)

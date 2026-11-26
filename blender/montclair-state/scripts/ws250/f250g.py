# ws250 pass 7 (CHAIN on ws250f): st250b found the crease lines' cause: the fan n-gons (5-7 verts, several collinear along an
# edge) subdivide into DEGENERATE folded quads (6.6 m x ~0 m, area 0.09 m2) along straight lines; their corner angles wreck
# the smooth vertex normals = the dark lines. Triangulate (BEAUTY, n-gons and quads) the separated piece after the weld and
# before the subdivide, so children are well-formed triangles.
import bpy
TAG='F250G'; ng=bpy.data.node_groups['WS250_W63_LiDAR_terrain_snap']; N=ng.nodes; L=ng.links
if 'WS250_triangulate' not in N:
    sd=N['WS250_subdiv']; src=sd.inputs['Mesh'].links[0].from_socket
    tr=N.new('GeometryNodeTriangulate'); tr.name='WS250_triangulate'
    try: tr.quad_method='BEAUTY'; tr.ngon_method='BEAUTY'
    except Exception as e: print(TAG,'props',e)
    for nm,val in (('Quad Method','Beauty'),('N-gon Method','Beauty')):
        if nm in tr.inputs:
            try: tr.inputs[nm].default_value=val
            except Exception as e: print(TAG,'inp',nm,e)
    L.new(src,tr.inputs['Mesh']); L.new(tr.outputs[0],sd.inputs['Mesh']); print(TAG,'triangulate inserted',[i.name for i in tr.inputs],flush=True)

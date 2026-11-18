import bpy, numpy as np
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(c): p = np.array(c[:2]) - A; return float(p @ n), float(p @ d)
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    m = o.matrix_world; hits = 0; mats = set()
    for f in o.data.polygons:
        c = m @ f.center; s, u = su(c)
        if 9.3 < s < 51 and -1.2 < u < 0.6 and 125 < c.z < 131:
            hits += 1; mats.add(o.data.materials[f.material_index].name if o.data.materials else None)
    if hits: print('HIT', o.name, hits, mats, o.library)
# walls material nodes
mt = bpy.data.materials['Wall_stucco_mission']
print('NODES', [(nd.type, nd.name, getattr(nd,'image',None) and nd.image.name) for nd in mt.node_tree.nodes])

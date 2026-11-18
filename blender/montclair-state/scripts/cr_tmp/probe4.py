import bpy, numpy as np
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(c): p = np.array(c[:2]) - A; return float(p @ n), float(p @ d)
o = bpy.data.objects['Alexander Kasser Theater walls']; me = o.data; m = o.matrix_world
print('PROPS', {k: o[k] for k in o.keys() if not k.startswith('_')})
fa = me.attributes['facade'].data
for f in me.polygons:
    c = m @ f.center; s, u = su(c)
    if 8 < s < 53 and -0.5 < u < 1.5 and c.z < 131.5:
        pts = [(round(su(m @ me.vertices[me.loops[li].vertex_index].co)[0], 2), round((m @ me.vertices[me.loops[li].vertex_index].co).z, 2), tuple(round(x, 2) for x in fa[li].vector)) for li in f.loop_indices]
        print('F', f.index, pts)

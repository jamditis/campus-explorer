import bpy, numpy as np, collections
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(c): p = np.array(c[:2]) - A; return float(p @ n), float(p @ d)
for on in ['Alexander Kasser Theater walls','Alexander Kasser Theater roof (LiDAR)']:
    o = bpy.data.objects[on]; m = o.matrix_world; me = o.data
    print('OBJ', on, len(me.polygons), [x.name if x else None for x in me.materials])
    cnt = collections.defaultdict(list)
    for f in me.polygons:
        c = m @ f.center; s, u = su(c)
        if 8 < s < 54 and -1.5 < u < 1.5 and 124 < c.z < 131.5:
            nw = m.to_3x3() @ f.normal
            cnt[me.materials[f.material_index].name].append((round(s,2), round(u,3), round(c.z,2), round(f.area,3), round(float(nw.x*d[0]+nw.y*d[1]),2)))
    for k, v in cnt.items():
        v.sort(); print(' MAT', k, len(v), 's range', v[0][0], v[-1][0], 'u', min(x[1] for x in v), max(x[1] for x in v), 'z', min(x[2] for x in v), max(x[2] for x in v))
        if len(v) < 400: print('   sample', v[:: max(1, len(v)//25)])
print('OBJS with Kasser', [o.name for o in bpy.data.objects if 'asser' in o.name])
print('pergola?', [o.name for o in bpy.data.objects if any(k in o.name.lower() for k in ('pergola','amphi','arch','trellis','gazebo','plaza'))])

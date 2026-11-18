import bpy, bmesh, numpy as np
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
for on in ('Alexander Kasser Theater roof (LiDAR)', 'Alexander Kasser Theater walls'):
    o = bpy.data.objects[on]; me = o.data; names = [m.name if m else None for m in me.materials]
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    rows = []
    for f in bm.faces:
        nm = names[f.material_index] or ''
        if not any(k in nm.lower() for k in ('glass', 'louv', 'door', 'frame')): continue
        ss = [su(v.co) for v in f.verts]; s_ = [a for a, b in ss]; u_ = [b for a, b in ss]; z_ = [v.co.z for v in f.verts]
        if max(z_) > 131.6 or min(u_) < -2.0 or max(u_) > 1.0 or max(s_) < 0 or min(s_) > 56: continue
        if 'glass' in nm.lower() and abs(f.normal.z) < 0.2: rows.append((round(min(s_), 2), round(max(s_), 2), round(min(u_), 3), round(min(z_), 2), round(max(z_), 2), nm))
    rows = sorted(set(rows))
    print('OBJ', on, len(rows))
    for r in rows: print('  ', r)

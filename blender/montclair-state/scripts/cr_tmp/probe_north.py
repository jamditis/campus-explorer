import bpy, numpy as np
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(c): p = np.array(c[:2]) - A; return float(p @ n), float(p @ d)
for o in bpy.data.objects:
    if o.type != 'MESH' or o.name.startswith('NT_') or 'grass' in o.name.lower(): continue
    bb = [o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
    S = [su(v)[0] for v in bb]; U = [su(v)[1] for v in bb]; Z = [v.z for v in bb]
    cs_, cu_ = (max(S)+min(S))/2, (max(U)+min(U))/2
    if 50 < cs_ < 130 and -60 < cu_ < 15:
        print('NEAR', o.name, 's %.1f..%.1f u %.1f..%.1f z %.1f..%.1f' % (min(S), max(S), min(U), max(U), min(Z), max(Z)), o.library is not None)

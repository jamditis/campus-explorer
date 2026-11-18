"""Session cg read-only probe: Kasser roof (LiDAR) faces near the RHD SE core, in (s,u) coords of the cf trim (s = into Kasser from the OSM shared edge, u = along A->B)."""
import bpy, numpy as np
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
o = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']
M = o.matrix_world; me = o.data
print('CG roof verts', len(me.vertices), 'faces', len(me.polygons), 'mats', [m.name for m in me.materials if m])
V = np.array([tuple(M @ v.co) for v in me.vertices])
P = V[:, :2] - A; S = P @ n; U = P @ d
print('CG roof s range', S.min().round(2), S.max().round(2), 'u range', U.min().round(2), U.max().round(2), 'z', V[:,2].min().round(2), V[:,2].max().round(2))
rows = []
for p in me.polygons:
    c = M @ p.center; nz = (M.to_3x3() @ p.normal).normalized().z
    pc = np.array([c.x, c.y]) - A; s = pc @ n; u = pc @ d
    rows.append((p.index, s, u, c.z, nz, p.material_index, p.area))
R = np.array(rows)
np.save('/workspace/nj-scenes/montclair-state/data/cg/roof_faces_cg.npy', R)
sel = R[(R[:,1] < 20) & (R[:,2] > -5) & (R[:,2] < 25)]
print('CG faces near core', len(sel))
steep = sel[np.abs(sel[:,4]) < 0.7]
print('CG steep faces (|nz|<0.7) near core', len(steep))
for r in steep[np.argsort(steep[:,2])][:80]: print('CG st idx %d s %.2f u %.2f z %.2f nz %.2f mat %d a %.2f' % tuple(r))
# height profile grid s 0..20 by u -2..24
for u0 in range(-2, 24, 2):
    line = []
    for s0 in range(0, 20, 1):
        m = (np.abs(R[:,1]-s0-0.5)<0.5)&(np.abs(R[:,2]-u0-1)<1)
        line.append('%6.2f' % R[m,3].max() if m.any() else '   -  ')
    print('CG prof u%3d ' % u0 + ' '.join(line))

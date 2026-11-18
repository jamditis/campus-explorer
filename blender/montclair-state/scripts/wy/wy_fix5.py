"""wy fix5 (review): clear wh_edge on the filled Reid hole and its old rim.

wh_edge mixes the WF patch's shading normal toward the coarse skirt (session wh,
12 m outer fade). The hole perimeter and the y=320 tile edge were exterior when
that attribute was painted, so they still shade as a dark crease — matching the
black crack in the south-eye and close-up views. Now that the sliver is filled
and WU/WT meet this edge, those verts are interior. Same treatment as wo/wn/wj
after they closed a gap: lower wh_edge. No vertex moves.
"""
import bpy, json, os, numpy as np
from collections import deque

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
SAVE = os.environ.get('SAVE') == '1'
PN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
X0, Y0 = 50.0, 320.0
O = bpy.data.objects
P = O[PN]
me = P.data
rep = json.load(open('data/wy/fix_report.json'))

M = np.load('data/wf/patch_mask.npz')
inside = M['inside_b']
H, W = inside.shape
vis = np.zeros_like(inside, dtype=bool)
reid = None
for j in range(H):
    for i in range(W):
        if not inside[j, i] or vis[j, i]:
            continue
        q = deque([(j, i)]); vis[j, i] = True; cells = []
        while q:
            y, x = q.popleft(); cells.append((y, x))
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and inside[yy, xx] and not vis[yy, xx]:
                    vis[yy, xx] = True; q.append((yy, xx))
        ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
        if min(ys) == 0 and (X0 + min(xs)) < 120:
            reid = dict(cells=cells, xmin=X0 + min(xs), xmax=X0 + max(xs),
                        ymin=Y0 + min(ys), ymax=Y0 + max(ys))
            break
if reid is None:
    raise SystemExit('Reid component not found')

near = set()
for j, i in reid['cells']:
    for dj in range(-8, 9):
        for di in range(-8, 9):
            near.add((i + di, j + dj))

a = me.attributes.get('wh_edge')
if a is None or a.domain != 'POINT':
    raise SystemExit('no wh_edge')
n = 0; before = []
for vi, v in enumerate(me.vertices):
    i = int(round(v.co.x - X0)); j = int(round(v.co.y - Y0))
    # hole + rim, or the y=320 tile edge across the hole's x span
    on_seam = (abs(v.co.y - 320.0) <= 8.0 and (reid['xmin'] - 4) <= v.co.x <= (reid['xmax'] + 4))
    if (i, j) not in near and not on_seam:
        continue
    old = float(a.data[vi].value)
    if old > 1e-4:
        before.append(old)
        a.data[vi].value = 0.0
        n += 1
rep['fix5_wh_edge'] = dict(
    cleared=n,
    prev=[round(float(min(before)), 4), round(float(np.median(before)), 4),
          round(float(max(before)), 4)] if before else None)
print('WH_EDGE cleared', rep['fix5_wh_edge'], flush=True)
json.dump(rep, open('data/wy/fix_report.json', 'w'), indent=1)
if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED', flush=True)

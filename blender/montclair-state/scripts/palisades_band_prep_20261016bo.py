"""2026-10-16 bo2: Palisades ridge low-rise band for the CCOM lab-window skyline.
Input: jersey-city-hoboken/data/lidar_sandy2014/palisades_heights_20261016bo.json (OSM footprints ODbL + USGS LPC Sandy 2014 LiDAR,
per-footprint roof p85 - ring ground; MEASURED). Output: data/ccom_mid_distance/bo/palisades_local_20261016bo.json in the
item format of the bo fill script (local EPSG:6527 frame). Ground = LiDAR ring ground (NAVD88 m, MEASURED). Drops buildings already
in the bn (tall) / bo (OSM mid-rise) sets, h<4 m, and roofs below the 3DEP terrain horizon from the lab cam (same test as bo)."""
import json, math, sys
sys.path.insert(0, '/workspace/nj-scenes/blender_pylib_proj')
import numpy as np
from pyproj import Transformer
import importlib.util
B = '/workspace/nj-scenes/montclair-state/data/ccom_mid_distance/'
T = Transformer.from_crs(4326, 6527, always_xy=True); E0, N0 = 575880.0, 738340.0; K = 1200 / 3937
R, KR = 6371000.0, 0.13
def drop(d): return d * d / (2 * R) * (1 - KR)
CAM = (26.98, -13.05, 140.62)
Dz = np.load('/workspace/nj-scenes/assets/backdrop_data/far/dem30_local.npz'); A = Dz['dem']; fx0, fx1, fy0, fy1 = [float(Dz[k]) for k in ('x0', 'x1', 'y0', 'y1')]
ny_, nx_ = A.shape
def dem(x, y):
    if not (fx0 < x < fx1 and fy0 < y < fy1): return None
    j = int((x - fx0) / (fx1 - fx0) * nx_); i = int((fy1 - y) / (fy1 - fy0) * ny_); v = float(A[min(i, ny_-1), min(j, nx_-1)])
    return v if v > -50 else None
BR0 = 90.0; BR = np.arange(BR0, 160.01, 0.1); DS = np.arange(300.0, 30001.0, 30.0); HZ = np.full((len(BR), len(DS)), -1.0)
for a, b in enumerate(BR):
    s, c = math.sin(math.radians(b)), math.cos(math.radians(b)); m = -1.0
    for k, d in enumerate(DS):
        z = dem(CAM[0] + s * d, CAM[1] + c * d)
        if z is not None:
            ang = (z - drop(d) - CAM[2]) / d; m = max(m, ang)
        HZ[a, k] = m
skip = set(o['id'] for o in json.load(open(B + 'bn/osm_tall_local_20261016bn.json'))['items']) | set(o['id'] for o in json.load(open(B + 'bo/osm_mid_local_20261016bo.json'))['items'])
L = json.load(open('/workspace/nj-scenes/jersey-city-hoboken/data/lidar_sandy2014/palisades_heights_20261016bo.json'))
out = []; why = {}
def no(k): why[k] = why.get(k, 0) + 1
for it in L['items']:
    if it['id'] in skip: no('dupe'); continue
    if it['h'] < 4.0: no('low'); continue
    P = [T.transform(a, b) for a, b in it['poly']]; P = [((x - E0) * K, (y - N0) * K) for x, y in P]
    if P[0] == P[-1]: P = P[:-1]
    Q = [P[0]]
    for q in P[1:]:
        if math.hypot(q[0] - Q[-1][0], q[1] - Q[-1][1]) > 1.5: Q.append(q)
    if len(Q) < 3: no('short'); continue
    ar = 0.5 * sum(Q[i][0] * Q[(i+1) % len(Q)][1] - Q[(i+1) % len(Q)][0] * Q[i][1] for i in range(len(Q)))
    if ar < 0: Q = Q[::-1]
    cx = sum(p[0] for p in Q) / len(Q); cy = sum(p[1] for p in Q) / len(Q); dx, dy = cx - CAM[0], cy - CAM[1]
    d = math.hypot(dx, dy); brg = (math.degrees(math.atan2(dx, dy)) + 360) % 360
    if not (BR0 <= brg <= 160): no('wedge'); continue
    top = (it['ground'] - drop(d) + it['h'] - CAM[2]) / d
    a = int(round((brg - BR0) / 0.1)); k = max(0, min(len(DS) - 1, int((d - 300.0) / 30.0) - 3))
    if top <= HZ[a, k]: no('below_horizon'); continue
    out.append(dict(id=it['id'], poly=[(round(x, 2), round(y, 2)) for x, y in Q], h=it['h'], hsrc='lidar_sandy2014_p85', gz=it['ground'], gsrc='lidar_class2_ring',
                    dist_m=round(d, 1), brg=round(brg, 2), mat='', colour='', grp='NJ_Palisades'))
json.dump(dict(tag='20261016bo2', source='OSM footprints (ODbL) + USGS LPC NJ Sandy 2014 LiDAR (public domain), heights MEASURED', cam=CAM, n=len(out), levels_only=0, rejected=why, items=out),
          open(B + 'bo/palisades_local_20261016bo.json', 'w'))
print('n', len(out), why)
if out:
    hs = sorted(o['h'] for o in out); ds = sorted(o['dist_m'] for o in out); print('h p10/50/90', hs[len(hs)//10], hs[len(hs)//2], hs[9*len(hs)//10], 'dist p50', ds[len(ds)//2])

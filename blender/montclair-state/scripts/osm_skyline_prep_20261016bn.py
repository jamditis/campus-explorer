"""2026-10-16 bn: prep OSM tall buildings (height>=45 m or levels>=14) for the CCOM lab-window skyline fill.
Input: data/ccom_mid_distance/bn/osm_tall_20261016bn.json (Overpass, ODbL, (c) OpenStreetMap contributors).
Output: data/ccom_mid_distance/bn/osm_tall_local_20261016bn.json in the EPSG:6527 local metre frame (origin E575880 N738340 ftUS),
same transform as assets/backdrop_data/prep_backdrop.py. Ground z from 3DEP dem30_local.npz where covered (MEASURED ~30 m px),
else group default (Manhattan 10 / NJ 5, UNVERIFIED). Height: OSM height tag (MEASURED-ish, NYC DOB/LiDAR import) or levels*3.6 m (UNVERIFIED).
Footprints thinned (vertices <2 m apart dropped). Landmarks already in the asset (within 60 m) are skipped. Idempotent (pure function of inputs)."""
import json, math, sys
sys.path.insert(0, '/workspace/nj-scenes/blender_pylib_proj')
import numpy as np
from pyproj import Transformer
B = '/workspace/nj-scenes/montclair-state/data/ccom_mid_distance/bn/'
T = Transformer.from_crs(4326, 6527, always_xy=True); E0, N0 = 575880.0, 738340.0; K = 1200 / 3937
D = json.load(open(B + 'osm_tall_20261016bn.json'))
BD = json.load(open('/workspace/nj-scenes/assets/backdrop_data/backdrop.json'))
LM = [(l['x'], l['y']) for l in BD['landmarks']]
Dz = np.load('/workspace/nj-scenes/assets/backdrop_data/far/dem30_local.npz'); A = Dz['dem']; fx0, fx1, fy0, fy1 = [float(Dz[k]) for k in ('x0', 'x1', 'y0', 'y1')]
ny_, nx_ = A.shape
def dem(x, y):
    if not (fx0 < x < fx1 and fy0 < y < fy1): return None
    j = int((x - fx0) / (fx1 - fx0) * nx_); i = int((fy1 - y) / (fy1 - fy0) * ny_); v = float(A[min(i, ny_-1), min(j, nx_-1)])
    return v if v > -50 else None
def num(s):
    try: return float(str(s).split(';')[0].replace('m', '').strip())
    except Exception: return None
def dp(P, eps):
    if len(P) < 3: return P
    a, b = np.array(P[0]), np.array(P[-1]); ab = b - a; L = np.hypot(*ab) or 1e-9
    d = [abs(np.cross(ab, np.array(p) - a)) / L for p in P[1:-1]]
    i = int(np.argmax(d)) + 1
    if d[i-1] > eps: return dp(P[:i+1], eps)[:-1] + dp(P[i:], eps)
    return [P[0], P[-1]]
out = []; skip_lm = 0; nlev = 0; ndem = 0
for e in D['elements']:
    if e['type'] != 'way' or 'geometry' not in e: continue
    t = e.get('tags', {}); h = num(t.get('height')); src = 'osm_height'
    if h is None:
        lv = num(t.get('building:levels'))
        if lv is None: continue
        h = lv * 3.6; src = 'levels*3.6_UNVERIFIED'; nlev += 1
    if h < 45 or h > 600: continue
    P = [T.transform(g['lon'], g['lat']) for g in e['geometry']]
    P = [((x - E0) * K, (y - N0) * K) for x, y in P]
    if P[0] == P[-1]: P = P[:-1]
    if len(P) < 3: continue
    Q = [P[0]]
    for q in P[1:]:
        if math.hypot(q[0] - Q[-1][0], q[1] - Q[-1][1]) > 2.0: Q.append(q)
    if len(Q) < 3: Q = P
    # ensure CCW
    ar = 0.5 * sum(Q[i][0] * Q[(i+1) % len(Q)][1] - Q[(i+1) % len(Q)][0] * Q[i][1] for i in range(len(Q)))
    if abs(ar) < 60: continue
    if ar < 0: Q = Q[::-1]
    cx = sum(p[0] for p in Q) / len(Q); cy = sum(p[1] for p in Q) / len(Q)
    if min(math.hypot(cx - a, cy - b) for a, b in LM) < 60: skip_lm += 1; continue
    lon = e['geometry'][0]['lon']; grp = 'Manhattan' if lon > -74.02 + (e['geometry'][0]['lat'] - 40.70) * 0.35 else 'NJ'
    gz = dem(cx, cy); gsrc = '3DEP30'
    if gz is None: gz = 10.0 if grp == 'Manhattan' else 5.0; gsrc = 'default_UNVERIFIED'
    else: ndem += 1
    d = math.hypot(cx, cy)
    out.append(dict(id=e['id'], name=t.get('name', ''), poly=[(round(x, 2), round(y, 2)) for x, y in Q], h=round(h, 1), hsrc=src, gz=round(gz, 2), gsrc=gsrc,
                    dist_m=round(d, 1), brg=round((math.degrees(math.atan2(cx, cy)) + 360) % 360, 2), mat=t.get('building:material', ''), colour=t.get('building:colour', ''), grp=grp))
json.dump(dict(tag='20261016bn', source='OpenStreetMap via overpass-api.de 2026-10-16 ~11:23 ET (ODbL)', n=len(out), skipped_landmark=skip_lm, levels_only=nlev, dem_ground=ndem, items=out), open(B + 'osm_tall_local_20261016bn.json', 'w'))
import collections
print('n', len(out), 'skip_lm', skip_lm, 'levels_only', nlev, 'dem', ndem, collections.Counter(o['grp'] for o in out))
hs = sorted(o['h'] for o in out); print('h p10/50/90/max', hs[len(hs)//10], hs[len(hs)//2], hs[9*len(hs)//10], hs[-1])
print('brg range', min(o['brg'] for o in out), max(o['brg'] for o in out), 'verts', sum(len(o['poly']) for o in out))

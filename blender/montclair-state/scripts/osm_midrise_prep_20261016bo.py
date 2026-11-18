"""2026-10-16 bo: prep OSM mid-rise buildings (height 15-45 m, or 4-13 levels w/o height) for the CCOM lab-window skyline.
Input: data/ccom_mid_distance/bo/osm_mid_20261016bo.json (Overpass, ODbL, (c) OpenStreetMap contributors), bbox 40.68..40.83 N, -74.10..-73.92 E.
Output: data/ccom_mid_distance/bo/osm_mid_local_20261016bo.json, same local frame/ground/curvature as the bn tall prep.
Kept only if: bearing 100..150 deg from the lab cam, distance 9..30 km, footprint >=60 m2, and the roof is ABOVE the terrain
horizon seen from the lab skyline cam (3DEP 30 m DEM ray march with the same curvature/refraction drop; MEASURED terrain,
building occlusion NOT tested). Heights: OSM height (MEASURED-ish) or levels*3.2+1 m (UNVERIFIED). Idempotent."""
import json, math, sys, collections
sys.path.insert(0, "/workspace/nj-scenes/blender_pylib_proj")
import numpy as np
from pyproj import Transformer
B = '/workspace/nj-scenes/montclair-state/data/ccom_mid_distance/bo/'
T = Transformer.from_crs(4326, 6527, always_xy=True); E0, N0 = 575880.0, 738340.0; K = 1200 / 3937
R, KR = 6371000.0, 0.13
def drop(d): return d * d / (2 * R) * (1 - KR)
CAM = (26.98, -13.05, 140.62)  # calibration_20261014y sky_cam (lab moved ~13 m later; negligible at >9 km)
Dz = np.load('/workspace/nj-scenes/assets/backdrop_data/far/dem30_local.npz'); A = Dz['dem']; fx0, fx1, fy0, fy1 = [float(Dz[k]) for k in ('x0', 'x1', 'y0', 'y1')]
ny_, nx_ = A.shape
def dem(x, y):
    if not (fx0 < x < fx1 and fy0 < y < fy1): return None
    j = int((x - fx0) / (fx1 - fx0) * nx_); i = int((fy1 - y) / (fy1 - fy0) * ny_); v = float(A[min(i, ny_-1), min(j, nx_-1)])
    return v if v > -50 else None
# horizon table: for bearing step 0.1 deg, running max elevation angle of terrain vs distance (step 30 m)
BR = np.arange(100.0, 150.01, 0.1); DS = np.arange(300.0, 30001.0, 30.0)
HZ = np.full((len(BR), len(DS)), -1.0)
for a, b in enumerate(BR):
    s, c = math.sin(math.radians(b)), math.cos(math.radians(b)); m = -1.0
    for k, d in enumerate(DS):
        z = dem(CAM[0] + s * d, CAM[1] + c * d)
        if z is not None:
            ang = (z - drop(d) - CAM[2]) / d
            if ang > m: m = ang
        HZ[a, k] = m
def num(s):
    try: return float(str(s).split(';')[0].replace('m', '').strip())
    except Exception: return None
D = json.load(open(B + 'osm_mid_20261016bo.json'))
out = []; why = collections.Counter(); nlev = 0
for e in D['elements']:
    if e['type'] != 'way' or 'geometry' not in e: continue
    t = e.get('tags', {}); h = num(t.get('height')); src = 'osm_height'
    if h is None:
        lv = num(t.get('building:levels'))
        if lv is None: why['noh'] += 1; continue
        h = lv * 3.2 + 1.0; src = 'levels*3.2+1_UNVERIFIED'
    if not (15 <= h < 45): why['hrange'] += 1; continue
    P = [T.transform(g['lon'], g['lat']) for g in e['geometry']]
    P = [((x - E0) * K, (y - N0) * K) for x, y in P]
    if P[0] == P[-1]: P = P[:-1]
    if len(P) < 3: why['short'] += 1; continue
    Q = [P[0]]
    for q in P[1:]:
        if math.hypot(q[0] - Q[-1][0], q[1] - Q[-1][1]) > 2.5: Q.append(q)
    if len(Q) < 3: Q = P
    ar = 0.5 * sum(Q[i][0] * Q[(i+1) % len(Q)][1] - Q[(i+1) % len(Q)][0] * Q[i][1] for i in range(len(Q)))
    if abs(ar) < 60: why['small'] += 1; continue
    if ar < 0: Q = Q[::-1]
    cx = sum(p[0] for p in Q) / len(Q); cy = sum(p[1] for p in Q) / len(Q)
    dx, dy = cx - CAM[0], cy - CAM[1]; d = math.hypot(dx, dy); brg = (math.degrees(math.atan2(dx, dy)) + 360) % 360
    if not (100 <= brg <= 150 and 9000 <= d <= 30000): why['wedge'] += 1; continue
    gz = dem(cx, cy); gsrc = '3DEP30'
    lon, lat = e['geometry'][0]['lon'], e['geometry'][0]['lat']
    grp = 'Manhattan' if lon > -74.02 + (lat - 40.70) * 0.35 else 'NJ'
    if gz is None: gz = 10.0 if grp == 'Manhattan' else 5.0; gsrc = 'default_UNVERIFIED'
    top = (gz - drop(d) + h - CAM[2]) / d
    a = int(round((brg - 100.0) / 0.1)); k = max(0, min(len(DS) - 1, int((d - 300.0) / 30.0) - 3))  # horizon up to ~90 m before the building
    if top <= HZ[a, k]: why['below_horizon'] += 1; continue
    if src != 'osm_height': nlev += 1
    out.append(dict(id=e['id'], poly=[(round(x, 2), round(y, 2)) for x, y in Q], h=round(h, 1), hsrc=src, gz=round(gz, 2), gsrc=gsrc,
                    dist_m=round(d, 1), brg=round(brg, 2), vis_margin_mrad=round((top - HZ[a, k]) * 1000, 3),
                    mat=t.get('building:material', ''), colour=t.get('building:colour', ''), roof=t.get('roof:colour', ''), grp=grp))
json.dump(dict(tag='20261016bo', source='OpenStreetMap via overpass-api.de 2026-10-16 ~12:30 ET (ODbL)', cam=CAM, n=len(out), levels_only=nlev,
               rejected=dict(why), items=out), open(B + 'osm_mid_local_20261016bo.json', 'w'))
print('n', len(out), 'levels_only', nlev, dict(why), collections.Counter(o['grp'] for o in out))
if out:
    hs = sorted(o['h'] for o in out); print('h p10/50/90', hs[len(hs)//10], hs[len(hs)//2], hs[9*len(hs)//10], 'verts', sum(len(o['poly']) for o in out))
    ds = sorted(o['dist_m'] for o in out); print('dist p10/50/90', ds[len(ds)//10], ds[len(ds)//2], ds[9*len(ds)//10])

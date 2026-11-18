"""wz probe (no save): diagnose the remaining y=320 south-seam black crack.

Uses per-object BVH trees (not scene.ray_cast). Samples the known near-black
pixels from the 20261108-1351 south-eye and close-up WY cameras (actual JPEG
is 1024x576 = 1280x720 @ 80%). Also measures WF/WU/WT open-edge positions
and heights along y≈320, x≈67–111.
"""
import bpy, json, os, math
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
WFN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
WUN = 'WU_richardson_reid_LiDAR_patch_UNVERIFIED'
WTN = 'WT_richardson_west_LiDAR_patch_UNVERIFIED'
SKN = 'Context_skirt_3DEP_ortho_4km'
TERRAIN = (WFN, WUN, WTN, SKN)
O = bpy.data.objects
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
rep = {}

def make_bvh(o):
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    verts = [o.matrix_world @ v.co for v in m.vertices]
    polys = [tuple(p.vertices) for p in m.polygons]
    b = BVHTree.FromPolygons(verts, polys)
    e.to_mesh_clear()
    return b

print('building BVHs...', flush=True)
BVH = {}
for n in TERRAIN:
    if O.get(n):
        BVH[n] = make_bvh(O[n])
        print('  BVH', n, flush=True)
print('BVHs ready', flush=True)

def hz(name, x, y):
    b = BVH.get(name)
    if not b:
        return None
    h = b.ray_cast(Vector((x, y, 500.0)), Vector((0.0, 0.0, -1.0)))
    return None if h[0] is None else float(h[0].z)

def closest_hit(origin, direction, dist=400.0):
    best = None
    for n, b in BVH.items():
        h = b.ray_cast(origin, direction, dist)
        if h[0] is None:
            continue
        rec = dict(obj=n,
                   xyz=[round(h[0].x, 4), round(h[0].y, 4), round(h[0].z, 4)],
                   nrm=[round(h[1].x, 4), round(h[1].y, 4), round(h[1].z, 4)],
                   dist=round(float(h[3]), 4),
                   face=int(h[2]))
        nd = direction.normalized().dot(h[1])
        rec['ndot'] = round(float(nd), 4)
        rec['backface'] = bool(nd > 0.05)
        if best is None or h[3] < best['dist']:
            best = rec
    return best

# ---- open-edge / height profile ----
def world_verts(obj):
    mw = obj.matrix_world
    return [mw @ v.co for v in obj.data.vertices]

def open_edges(obj, y0=320.0, ytol=0.6, x1=66.0, x2=112.0):
    me = obj.data
    mw = obj.matrix_world
    edge_count = defaultdict(int)
    for p in me.polygons:
        vs = list(p.vertices)
        for a, b in zip(vs, vs[1:] + vs[:1]):
            e = (a, b) if a < b else (b, a)
            edge_count[e] += 1
    rows = []
    for (a, b), c in edge_count.items():
        if c != 1:
            continue
        ca = mw @ me.vertices[a].co
        cb = mw @ me.vertices[b].co
        ym = 0.5 * (ca.y + cb.y)
        xm = 0.5 * (ca.x + cb.x)
        if abs(ym - y0) > ytol or not (x1 <= xm <= x2):
            continue
        # outward-ish: face-centroid vs edge
        rows.append(dict(
            x=round(float(xm), 3), y=round(float(ym), 3),
            z=round(float(0.5 * (ca.z + cb.z)), 4),
            dy=round(float(cb.y - ca.y), 3),
            dx=round(float(cb.x - ca.x), 3),
            za=round(float(ca.z), 4), zb=round(float(cb.z), 4),
            ya=round(float(ca.y), 3), yb=round(float(cb.y), 3),
            xa=round(float(ca.x), 3), xb=round(float(cb.x), 3),
        ))
    rows.sort(key=lambda r: r['x'])
    return rows

print('open edges...', flush=True)
oe = {}
for n in (WFN, WUN, WTN):
    oe[n] = open_edges(O[n])
    ys = [r['y'] for r in oe[n]]
    zs = [r['z'] for r in oe[n]]
    print(f'  OPEN {n.split("_")[0]} n={len(oe[n])}'
          f' y=[{min(ys):.3f},{max(ys):.3f}]' if ys else f'  OPEN {n} n=0',
          f'z=[{min(zs):.3f},{max(zs):.3f}]' if zs else '',
          flush=True)
rep['open_edges'] = {n.split('_')[0]: dict(
    n=len(oe[n]),
    y=[round(min(r['y'] for r in oe[n]), 3), round(max(r['y'] for r in oe[n]), 3)] if oe[n] else None,
    z=[round(min(r['z'] for r in oe[n]), 4), round(max(r['z'] for r in oe[n]), 4)] if oe[n] else None,
    sample=oe[n][::max(1, len(oe[n]) // 12)] if oe[n] else [],
) for n in (WFN, WUN, WTN)}

# height profile every 1 m
print('height profile...', flush=True)
prof = []
for x in [round(xx * 0.5, 2) for xx in range(134, 223)]:  # 67.0 .. 111.0 step 0.5
    rec = {'x': x}
    for y in (318.0, 319.0, 319.5, 320.0, 320.2, 320.35, 320.5, 321.0):
        rec[f'WF_y{y}'] = None if hz(WFN, x, y) is None else round(hz(WFN, x, y), 4)
        rec[f'WU_y{y}'] = None if hz(WUN, x, y) is None else round(hz(WUN, x, y), 4)
        rec[f'WT_y{y}'] = None if hz(WTN, x, y) is None else round(hz(WTN, x, y), 4)
    zf = rec.get('WF_y320.0')
    zu = rec.get('WU_y320.0')
    zt = rec.get('WT_y320.0')
    zs = [z for z in (zu, zt) if z is not None]
    rec['gap_WF_minus_south'] = None if (zf is None or not zs) else round(zf - max(zs), 4)
    rec['WU_at_320_35'] = rec.get('WU_y320.35')
    rec['WF_at_320'] = zf
    prof.append(rec)
rep['profile'] = prof
gaps = [r['gap_WF_minus_south'] for r in prof if r['gap_WF_minus_south'] is not None]
print('  gaps (WF - south sheet at y=320) n=', len(gaps),
      'min/med/max', (round(min(gaps), 4), round(sorted(gaps)[len(gaps)//2], 4), round(max(gaps), 4)) if gaps else None,
      flush=True)
# print a few
for r in prof[::8]:
    print('  PROF', {k: r[k] for k in ('x', 'WF_y320.0', 'WU_y320.0', 'WT_y320.0',
                                        'WU_y320.35', 'WU_y319.0', 'gap_WF_minus_south')},
          flush=True)

# southmost WF verts in band (should be the open lip)
print('WF south lip verts...', flush=True)
wf = O[WFN]
mw = wf.matrix_world
lip = []
for v in wf.data.vertices:
    c = mw @ v.co
    if abs(c.y - 320.0) <= 0.15 and 66.5 <= c.x <= 111.5:
        lip.append((float(c.x), float(c.y), float(c.z)))
lip.sort()
rep['wf_lip_n'] = len(lip)
rep['wf_lip_y'] = [round(min(p[1] for p in lip), 4), round(max(p[1] for p in lip), 4)] if lip else None
rep['wf_lip_z'] = [round(min(p[2] for p in lip), 4), round(max(p[2] for p in lip), 4)] if lip else None
print('  WF lip n', len(lip), 'y', rep['wf_lip_y'], 'z', rep['wf_lip_z'], flush=True)

# leftover attributes near the seam
print('attributes...', flush=True)
attr_sum = {}
for n in (WFN, WUN, WTN):
    me = O[n].data
    names = [a.name for a in me.attributes
             if a.domain == 'POINT' and a.data_type == 'FLOAT'
             and not a.name.startswith('.') and a.name != 'position']
    rec = {}
    mw = O[n].matrix_world
    for an in names:
        a = me.attributes[an]
        vals = []
        for vi, v in enumerate(me.vertices):
            c = mw @ v.co
            if not (66 <= c.x <= 112 and 317 <= c.y <= 323):
                continue
            val = float(a.data[vi].value)
            if abs(val) > 1e-5:
                vals.append(val)
        rec[an] = dict(nonzero=len(vals),
                       minmax=[round(min(vals), 4), round(max(vals), 4)] if vals else None)
    attr_sum[n.split('_')[0]] = {'names': names, 'near_seam': rec}
    print('  ATTR', n.split('_')[0], rec, flush=True)
rep['attrs'] = attr_sum

# ---- camera pixel rays ----
def pixel_ray(cam, px, py, resx=1024, resy=576):
    nx = (px + 0.5) / resx
    ny = 1.0 - (py + 0.5) / resy
    tr, br, bl, tl = cam.data.view_frame(scene=sc)
    top = tl.lerp(tr, nx)
    bot = bl.lerp(br, nx)
    p = bot.lerp(top, ny)
    origin = cam.matrix_world.translation.copy()
    target = cam.matrix_world @ p
    direction = (target - origin).normalized()
    return origin, direction

# known near-black crack pixels from the 1351 JPEGs (1024x576)
S_PIX = [
    (160, 322), (180, 323), (200, 325), (220, 323), (239, 322), (263, 322),
    (280, 323), (298, 323), (323, 325), (340, 328), (362, 332), (380, 334),
    (395, 335), (412, 338), (430, 342), (448, 345), (463, 348), (485, 351),
    (500, 353), (516, 355), (535, 357), (553, 359), (580, 361), (615, 362),
    (640, 363), (672, 363), (704, 364), (748, 365), (803, 366), (837, 367),
    (875, 368), (908, 369), (943, 370),
]
# off-crack comparison (20 px above the crack)
S_OK = [(x, y - 25) for x, y in S_PIX[::3]]

C_PIX = [
    (16, 497), (48, 485), (80, 478), (112, 464), (144, 448), (176, 436),
    (208, 426), (240, 411), (272, 402), (304, 386), (336, 374), (368, 365),
    (400, 358), (432, 349), (464, 340), (496, 337), (528, 334), (560, 328),
    (578, 325), (616, 317),
]
C_OK = [(x, y - 30) for x, y in C_PIX[::2] if y - 30 > 0]

def classify_pixels(cam_name, pixels, tag):
    cam = O[cam_name]
    out = []
    counts = defaultdict(int)
    print(f'rays {tag} {cam_name} n={len(pixels)}', flush=True)
    for px, py in pixels:
        origin, direction = pixel_ray(cam, px, py)
        hit = closest_hit(origin, direction)
        rec = dict(px=px, py=py,
                   origin=[round(origin.x, 3), round(origin.y, 3), round(origin.z, 4)],
                   dir=[round(direction.x, 4), round(direction.y, 4), round(direction.z, 4)])
        if hit is None:
            rec['cls'] = 'VOID'
            counts['VOID'] += 1
            # how close does this ray pass to the WF lip (y=320 plane)?
            # origin + t * dir, set y = 320
            if abs(direction.y) > 1e-6:
                t = (320.0 - origin.y) / direction.y
                if t > 0:
                    p = origin + t * direction
                    rec['at_y320'] = [round(p.x, 3), round(p.y, 3), round(p.z, 4)]
                    zf = hz(WFN, p.x, 320.0)
                    zu = hz(WUN, p.x, 320.0)
                    zt = hz(WTN, p.x, 320.0)
                    rec['WF_z'] = None if zf is None else round(zf, 4)
                    rec['WU_z'] = None if zu is None else round(zu, 4)
                    rec['WT_z'] = None if zt is None else round(zt, 4)
                    if zf is not None:
                        rec['under_WF_cm'] = round((zf - p.z) * 100.0, 2)
        else:
            rec['hit'] = hit
            rec['cls'] = 'BACKFACE' if hit['backface'] else 'HIT'
            counts[rec['cls']] += 1
            counts['hit:' + hit['obj'].split('_')[0]] += 1
        out.append(rec)
    print('  COUNTS', dict(counts), flush=True)
    # print voids and backfaces in full; a few hits
    for rec in out:
        if rec['cls'] != 'HIT':
            print('   ', rec['cls'], rec, flush=True)
    return out, dict(counts)

s_out, s_c = classify_pixels('WY_CAM_eye_reid_hole_from_S', S_PIX, 'crackS')
s_ok, s_okc = classify_pixels('WY_CAM_eye_reid_hole_from_S', S_OK, 'okS')
c_out, c_c = classify_pixels('WY_CAM_closeup_reid_hole_seam', C_PIX, 'crackC')
c_ok, c_okc = classify_pixels('WY_CAM_closeup_reid_hole_seam', C_OK, 'okC')

rep['south_eye_crack'] = dict(counts=s_c, rays=s_out)
rep['south_eye_ok'] = dict(counts=s_okc, rays=s_ok)
rep['closeup_crack'] = dict(counts=c_c, rays=c_out)
rep['closeup_ok'] = dict(counts=c_okc, rays=c_ok)

# summary of under-lip amounts
unders = [r.get('under_WF_cm') for r in s_out + c_out if r.get('under_WF_cm') is not None]
print('UNDER-LIP cm (void rays crossing y=320):',
      (round(min(unders), 2), round(sorted(unders)[len(unders)//2], 2), round(max(unders), 2)) if unders else None,
      'n', len(unders), flush=True)
rep['under_lip_cm'] = ([round(min(unders), 2), round(sorted(unders)[len(unders)//2], 2),
                        round(max(unders), 2)] if unders else None)

json.dump(rep, open('data/wz/probe.json', 'w'), indent=1)
print('WROTE data/wz/probe.json', flush=True)
print('NO SAVE', flush=True)

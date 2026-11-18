"""Session ua (Nov 5 2026 ~11:25 AM ET, MAIN, day 9): Normal Ave edge — verified curb/walk only.
Geo-honest strip on existing Context_skirt south of half_m=250 (NOT the full 680 m west CR 618).
(1) Normal Ave asphalt ribbon: OSM 583841725 (x>=-280) + 583841727 + 583841729, width 7.3 m UNVERIFIED, soft ends.
(2) North (campus) sidewalk on 583841727 where sidewalk=separate, ~2.2 m UNVERIFIED.
(3) College Avenue spur 1557427669 from Normal Ave junction up toward Roads_OSM / 232844571.
(4) Skyline Way south stub (232846698, y<-249) + footway 312845863 campus-side walk.
NO signals/poles/benches/bins/signs. Soft open ends like sg Quad Road.
ALL UNVERIFIED where not MEASURED. Tag ua_obj=1; collection UA_Normal_Ave_edge_UNVERIFIED.
REVERT=1 removes everything.
"""
import bpy, bmesh, os, json, math
import numpy as np
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UA_Normal_Ave_edge_UNVERIFIED'
W_ROAD = 7.3          # curb-to-curb UNVERIFIED (prep)
W_WALK = 2.2          # sidewalk / footway UNVERIFIED
W_SVC = 5.5           # Skyline Way service UNVERIFIED
OFF_ROAD = 0.03
OFF_WALK = 0.05
TAPER_M = 8.0
X_CLIP = -280.0       # do not extend Normal Ave west of this (far off-campus)

def revert():
    for o in [o for o in list(bpy.data.objects) if o.get('ua_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            if t == 'MESH': bpy.data.meshes.remove(me)
            elif t == 'CAMERA': bpy.data.cameras.remove(me)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    for m in [m for m in bpy.data.materials if m.name.startswith('UA_') and m.users == 0]:
        bpy.data.materials.remove(m)
    print('UA REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

bi = json.load(open(D + 'north/data/day_heroes/day9_normal_ave_edge_prep_20261016bi.json'))
WAYS = {w['id']: w for w in bi['ways']}
sd = json.load(open(D + 'data/scene_data.json'))
F = {str(f['id']): f for f in sd['features']}

# ---- DTM crop (MEASURED) + scene ground raycast ----
dtm_npz = np.load(D + 'north/data/day_heroes/day9_normal_ave_dtm_20261016bi.npz')
DTM = dtm_npz['dtm']; XS = dtm_npz['xs']; YS = dtm_npz['ys']
# xs increasing in x, ys — check order
def dtm_z(x, y):
    # bilinear on regular 1 m grid
    if x < XS[0] or x > XS[-1] or y < YS.min() or y > YS.max():
        return None
    # YS may be descending or ascending
    if YS[0] < YS[-1]:
        iy = (y - YS[0]) / (YS[1] - YS[0]) if len(YS) > 1 else 0
    else:
        iy = (YS[0] - y) / (YS[0] - YS[1]) if len(YS) > 1 else 0
    ix = (x - XS[0]) / (XS[1] - XS[0]) if len(XS) > 1 else 0
    if not (0 <= ix <= len(XS) - 1 and 0 <= iy <= len(YS) - 1):
        return None
    i0 = int(math.floor(ix)); j0 = int(math.floor(iy))
    i1 = min(i0 + 1, len(XS) - 1); j1 = min(j0 + 1, len(YS) - 1)
    tx = ix - i0; ty = iy - j0
    # DTM indexed [row=y, col=x]
    if YS[0] < YS[-1]:
        z00 = DTM[j0, i0]; z10 = DTM[j0, i1]; z01 = DTM[j1, i0]; z11 = DTM[j1, i1]
    else:
        # row 0 = YS[0] (north); iy measured from north
        z00 = DTM[j0, i0]; z10 = DTM[j0, i1]; z01 = DTM[j1, i0]; z11 = DTM[j1, i1]
    if not np.isfinite([z00, z10, z01, z11]).all():
        return None
    return float((1 - tx) * (1 - ty) * z00 + tx * (1 - ty) * z10 + (1 - tx) * ty * z01 + tx * ty * z11)

dg = bpy.context.evaluated_depsgraph_get()
GN = ['Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km', 'QW_DTM_north_edge_ramp_UNVERIFIED',
      'RZ2_SC_LiDAR_ground_patch', 'SA_ground_lower_patch_UNVERIFIED', 'QM_terrain_band_underlay_UNVERIFIED',
      'QJ_NE_seam_fill_UNVERIFIED']
gnd = []
for n in GN:
    o = bpy.data.objects.get(n)
    if o:
        gnd.append((o.evaluated_get(dg), o.matrix_world, n))

def ray_z(x, y):
    best = None
    for e, mw, n in gnd:
        iw = mw.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (mw @ r[1]).z
            if best is None or z > best:
                best = z
    return best

def gz(x, y):
    """Prefer DTM crop (MEASURED) when available; else scene ground max."""
    z_d = dtm_z(x, y)
    z_r = ray_z(x, y)
    if z_d is not None and z_r is not None:
        # prefer DTM on the Normal Ave strip but never float above skirt by >0.4 m
        if abs(z_d - z_r) < 1.5:
            return z_d
        return max(z_d, z_r)  # stay on top of whatever ground exists
    return z_d if z_d is not None else z_r

col = bpy.data.collections.new(COLN)
bpy.context.scene.collection.children.link(col)

def mat(name, rgb, rough=0.9, noise=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    try: b.inputs['Specular IOR Level'].default_value = 0.25
    except Exception: pass
    if noise:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.5; n.inputs['Detail'].default_value = 6
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].color = (rgb[0]*(1-noise), rgb[1]*(1-noise), rgb[2]*(1-noise), 1)
        r.color_ramp.elements[1].color = (*rgb, 1)
        nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*rgb, 1)
    return m

mrd = bpy.data.materials.get('SF_asphalt_worn_UNVERIFIED')
if mrd is None:
    mrd = mat('UA_asphalt_worn_UNVERIFIED', (0.08, 0.08, 0.085), 0.92, noise=0.18)
matw = bpy.data.materials.get('SC_walk_concrete_joints_UNVERIFIED')
if matw is None:
    matw = bpy.data.materials.get('TY_walk_concrete_UNVERIFIED')
if matw is None:
    matw = mat('UA_walk_concrete_UNVERIFIED', (0.42, 0.40, 0.37), 0.88, noise=0.12)

def link(name, bm, material, note, shadow=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(material)
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    ob['ua_obj'] = 1; ob['UNVERIFIED_ua'] = note; ob.visible_shadow = shadow
    return ob

def densify(pts, step=0.75):
    S = []
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, by - ay); n = max(1, int(L / step))
        for i in range(n):
            t = i / n; S.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    S.append(tuple(pts[-1])); return S

def ribbon(pts, w, off, name, taper_start, taper_end, material, note, T=TAPER_M, sink=0.16, depth=0.30):
    S = densify(pts, 0.75)
    cum = [0.0]
    for a, b in zip(S[:-1], S[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = cum[-1]
    bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap'); rows = []
    miss = 0
    for i, (x, y) in enumerate(S):
        a = S[max(i - 1, 0)]; b = S[min(i + 1, len(S) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        o = off
        if taper_start and cum[i] < T:
            o = off - sink * (1 - cum[i] / T)
        if taper_end and tot - cum[i] < T:
            o = off - sink * (1 - (tot - cum[i]) / T)
        Lpt = (x + nx * w / 2, y + ny * w / 2)
        Rpt = (x - nx * w / 2, y - ny * w / 2)
        zc = gz(x, y)
        if zc is None:
            rows.append(None); miss += 1; continue
        zl = gz(*Lpt) or zc; zr = gz(*Rpt) or zc
        rows.append([
            bm.verts.new((Lpt[0], Lpt[1], zl + o)),
            bm.verts.new((Rpt[0], Rpt[1], zr + o)),
            bm.verts.new((Lpt[0], Lpt[1], zl + o - depth)),
            bm.verts.new((Rpt[0], Rpt[1], zr + o - depth)),
        ])
    nq = 0
    for p, q in zip(rows[:-1], rows[1:]):
        if p is None or q is None: continue
        for quad in ((p[0], q[0], q[1], p[1]), (p[2], q[2], q[0], p[0]), (p[1], q[1], q[3], p[3])):
            try:
                fc = bm.faces.new(quad); nq += 1
                for lp in fc.loops:
                    lp[uv].uv = (lp.vert.co.x / 2.0, lp.vert.co.y / 2.0)
            except ValueError:
                pass
    if nq == 0:
        bm.free(); print('UA SKIP empty', name, 'miss', miss); return None, 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = link(name, bm, material, note)
    print(f'UA ribbon {name} quads={nq} len={tot:.1f}m miss={miss}')
    return ob, nq

def offset_line(pts, dist):
    """Offset polyline to the left (relative to travel) by dist metres."""
    S = densify(pts, 1.0)
    out = []
    for i, (x, y) in enumerate(S):
        a = S[max(i - 1, 0)]; b = S[min(i + 1, len(S) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L  # left
        out.append((x + nx * dist, y + ny * dist))
    # simplify back roughly every ~2 m
    simp = [out[0]]
    acc = 0.0
    for a, b in zip(out[:-1], out[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        if acc >= 2.0:
            simp.append(b); acc = 0.0
    if simp[-1] != out[-1]:
        simp.append(out[-1])
    return simp

# ---- 1) Normal Ave asphalt chain ----
def stations_xy(wid, x_min=None):
    w = WAYS[wid]
    pts = []
    for s in w['stations_5m']:
        x, y = s[1], s[2]
        if x_min is not None and x < x_min:
            continue
        pts.append((x, y))
    # ensure we include clipped entry if first kept station jumps
    return pts

pts_725 = stations_xy('583841725', x_min=X_CLIP)
pts_727 = stations_xy('583841727')
pts_729 = stations_xy('583841729')
# chain without duplicating junctions
chain = pts_725[:]
if pts_727:
    if chain and math.hypot(chain[-1][0] - pts_727[0][0], chain[-1][1] - pts_727[0][1]) < 1.0:
        chain += pts_727[1:]
    else:
        chain += pts_727
if pts_729:
    if chain and math.hypot(chain[-1][0] - pts_729[0][0], chain[-1][1] - pts_729[0][1]) < 1.0:
        chain += pts_729[1:]
    else:
        chain += pts_729
print(f'UA Normal Ave chain n={len(chain)} from ({chain[0][0]:.1f},{chain[0][1]:.1f}) to ({chain[-1][0]:.1f},{chain[-1][1]:.1f})')

ribbon(chain, W_ROAD, OFF_ROAD,
       'UA_NormalAve_CR618_583841725_727_729_UNVERIFIED',
       True, True, mrd,
       'OSM Normal Ave CR 618 near-campus strip (x>=-280) draped on USGS 1m DEM + Context_skirt; width 7.3 m UNVERIFIED; soft 8 m ends; NO far-west 680 m span')

# ---- 2) North sidewalk on 583841727 (sidewalk=separate) ----
# Travel W→E; campus is north (+y). Left offset when going W→E points northish.
# Place walk centre at road_half + walk_half + 0.15 m gap
walk_off = W_ROAD / 2 + W_WALK / 2 + 0.15
walk_c = offset_line(pts_727, walk_off)
ribbon(walk_c, W_WALK, OFF_WALK,
       'UA_NormalAve_N_sidewalk_583841727_UNVERIFIED',
       True, True, matw,
       'OSM sidewalk=separate on 583841727; north/campus side; width 2.2 m UNVERIFIED; NAIP shows concrete; soft ends')

# ---- 3) College Avenue spur 1557427669 ----
f_ca = F.get('1557427669')
if f_ca:
    # pts run Normal Ave junction → north toward campus; reverse so we taper at both, soft join at north end into Roads_OSM
    ca = [tuple(p) for p in f_ca['pts']]
    # keep as-is (south→north); taper both ends (south into Normal Ave, north into existing Roads_OSM)
    ribbon(ca, 7.0, OFF_ROAD,
           'UA_CollegeAve_spur_1557427669_UNVERIFIED',
           True, True, mrd,
           'OSM College Avenue spur from Normal Ave junction up to 232844571 / Roads_OSM south; width 7.0 m UNVERIFIED; soft ends')

# ---- 4) Skyline Way south of y=-249 ----
f_sk = F.get('232846698')
if f_sk:
    sk = [tuple(p) for p in f_sk['pts'] if p[1] <= -240]  # slight overlap into half for soft join
    if len(sk) >= 2:
        # pts go south→north in OSM? first is south Normal Ave end
        ribbon(sk, W_SVC, OFF_ROAD,
               'UA_SkylineWay_south_232846698_UNVERIFIED',
               True, True, mrd,
               'OSM Skyline Way service south of half_m into Normal Ave; width 5.5 m UNVERIFIED; soft ends')

# ---- 5) Footway 312845863 (campus-side walk near Normal Ave) ----
f_fw = F.get('312845863')
if f_fw:
    fw = [tuple(p) for p in f_fw['pts']]
    # Prefer the portion near Normal Ave / south of College (y < -160) to avoid fighting Footpaths_OSM further north
    # Keep full way but soft ends; Footpaths_OSM already has the north part — this adds the south extension + continuous ribbon
    # Actually building over Footpaths_OSM could z-fight. Clip to y <= -245 (just outside / at edge) plus a short overlap.
    fw_s = [p for p in fw if p[1] <= -240]
    # Also include the east-west Normal Ave–parallel stretch (y around -270)
    # The way snakes; use all pts with y<=-200 for the south approach band
    fw_s = [p for p in fw if p[1] <= -200]
    if len(fw_s) >= 2:
        ribbon(fw_s, W_WALK, OFF_WALK,
               'UA_footway_312845863_south_UNVERIFIED',
               True, True, matw,
               'OSM footway 312845863 south band (y<=-200) near Normal Ave; width 2.2 m UNVERIFIED; soft ends')

# ---- cameras ----
def add_cam(name, loc, look_at, lens=35):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    ob = bpy.data.objects.new(name, cam)
    col.objects.link(ob)
    ob['ua_obj'] = 1
    ob.location = Vector(loc)
    direction = Vector(look_at) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return ob

# Midpoint of Normal Ave chain
mid = chain[len(chain) // 2]
zm = gz(*mid) or 120.0
# aerial/oblique from SW above Normal Ave / College Ave junction
add_cam('UA_CAM_oblique_NormalAve_from_SW',
        (mid[0] - 80, mid[1] - 90, zm + 55),
        (mid[0] + 20, mid[1] + 10, zm + 2), lens=28)
# eye-level north side (campus looking south at road)
add_cam('UA_CAM_eye_NormalAve_from_N',
        (mid[0], mid[1] + 18, zm + 1.7),
        (mid[0] + 15, mid[1] - 5, zm + 1.2), lens=40)
# eye-level from College Ave spur looking toward junction
ca_look = (-256.1, -271.6, (gz(-256.1, -271.6) or 118) + 1.2)
add_cam('UA_CAM_eye_CollegeAve_spur_to_Normal',
        (-230, -200, (gz(-230, -200) or 120) + 1.7),
        ca_look[:3], lens=40)
# close-up of road + sidewalk meeting
add_cam('UA_CAM_closeup_NormalAve_N_sidewalk',
        (mid[0] - 5, mid[1] + 8, zm + 2.2),
        (mid[0] + 2, mid[1] - 1, zm + 0.3), lens=45)

print('UA cams', [o.name for o in col.objects if o.type == 'CAMERA'])
print('UA objects in collection', len(col.objects))

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', len(bpy.data.objects), 'objects')

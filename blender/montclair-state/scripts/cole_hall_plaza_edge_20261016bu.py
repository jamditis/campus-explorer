"""tag 20261016bu: Cole Hall plaza edge — steps/railings, smooth mulch beds, addition forecourt.

Idempotent. SAVE=1 to write. Flag/prop: bu_cole_plaza_edge on Terrain_LiDAR_DTM_1m.
Collection: COLE_plaza_edge_20261016bu.

Evidence:
- West edge of COLE_plaza_deck_bs (x≈−199, y −100…−57) toward Kasser drive (asphalt ~x −220).
  LiDAR DTM drop ~1.5 m at y≈−95 (MEASURED); riser count / tread / rail form UNVERIFIED
  (style from Susan_Cole_Hall_.jpg eye-ref + ortho2020 west-edge walkway).
- Planting beds COLE_planting_mulch_bs were stair-stepped 1 m terrain cells (bs). Replace with a
  smooth outline mesh; revert terrain mulch faces → lawn so lawn/ortho logic stays intact.
- 2020 north-addition entrance forecourt: spring ortho still construction; build a small curved
  red-band apron on Cole axis (from scene_data OSM long edge) matching plaza paver mats. Pitch UNVERIFIED.
"""
import bpy, bmesh, os, json, math, statistics
from mathutils import Vector
from mathutils.bvhtree import BVHTree

TAG = "bu"
FLAG = "bu_cole_plaza_edge"
COLN = "COLE_plaza_edge_20261016bu"
here = os.path.dirname(bpy.data.filepath)
T = bpy.data.objects["Terrain_LiDAR_DTM_1m"]
me = T.data
dg = bpy.context.evaluated_depsgraph_get()
bv_t = BVHTree.FromObject(T, dg)
deck = bpy.data.objects.get("COLE_plaza_deck_bs")
assert deck is not None, "need COLE_plaza_deck_bs (run bs ground first)"
bv_d = BVHTree.FromObject(deck, dg)

def ground_z(x, y, prefer_deck=False):
    if prefer_deck:
        h = bv_d.ray_cast(Vector((x, y, 200)), Vector((0, 0, -1)))
        if h[0] is not None:
            return h[0].z
    h = bv_t.ray_cast(Vector((x, y, 200)), Vector((0, 0, -1)))
    return h[0].z if h[0] is not None else None

def cole_axis_deg():
    d = json.load(open(os.path.join(here, "data", "scene_data.json")))
    for f in d["features"]:
        if f["id"] == "312932811":
            p = f["pts"]; best = (0, 0)
            for a, b in zip(p, p[1:] + p[:1]):
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                if L > best[0]:
                    best = (L, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])))
            return best[1]
    return -14.0

ang = cole_axis_deg()
print("COLE_AXIS_DEG", round(ang, 2))

# ---------- collection / clean prior ----------
col = bpy.data.collections.get(COLN)
if col is None:
    col = bpy.data.collections.new(COLN)
    bpy.context.scene.collection.children.link(col)
for o in list(col.objects):
    m = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    if m and getattr(m, "users", 1) == 0:
        if isinstance(m, bpy.types.Mesh):
            bpy.data.meshes.remove(m)

def link(ob):
    col.objects.link(ob)
    return ob

# ---------- materials ----------
def mat_concrete():
    m = bpy.data.materials.get("COLE_plaza_steps_bu")
    if m:
        return m
    m = bpy.data.materials.new("COLE_plaza_steps_bu")
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.34, 0.33, 0.315, 1)
    bs.inputs["Roughness"].default_value = 0.88
    m["bu_note"] = "step/tread concrete UNVERIFIED tone"
    return m

def mat_rail():
    m = bpy.data.materials.get("COLE_plaza_rail_bu")
    if m:
        return m
    m = bpy.data.materials.new("COLE_plaza_rail_bu")
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.04, 0.04, 0.045, 1)
    bs.inputs["Roughness"].default_value = 0.35
    bs.inputs["Metallic"].default_value = 0.85
    m["bu_note"] = "dark metal handrail UNVERIFIED; style from Susan_Cole_Hall_.jpg eye-ref"
    return m

def mat_mulch_smooth():
    # reuse bs mulch look if present
    src = bpy.data.materials.get("COLE_planting_mulch_bs")
    m = bpy.data.materials.get("COLE_planting_mulch_smooth_bu")
    if m:
        return m
    if src:
        m = src.copy()
        m.name = "COLE_planting_mulch_smooth_bu"
    else:
        m = bpy.data.materials.new("COLE_planting_mulch_smooth_bu")
        m.use_nodes = True
        bs = m.node_tree.nodes["Principled BSDF"]
        bs.inputs["Base Color"].default_value = (0.05, 0.03, 0.02, 1)
        bs.inputs["Roughness"].default_value = 0.95
    m["bu_note"] = "smoothed planting-bed mesh (outline UNVERIFIED); replaces stair-step terrain mulch"
    return m

def mat_paver(ang_deg):
    # Prefer share with plaza; else copy nodes from COLE_plaza_pavers_bs
    m = bpy.data.materials.get("COLE_add_forecourt_pavers_bu")
    if m:
        return m
    src = bpy.data.materials.get("COLE_plaza_pavers_bs")
    if src:
        m = src.copy()
        m.name = "COLE_add_forecourt_pavers_bu"
        m["bu_note"] = f"addition forecourt pavers + red bands on Cole axis {ang_deg:.1f} deg; pattern pitch UNVERIFIED"
        return m
    # minimal fallback
    m = bpy.data.materials.new("COLE_add_forecourt_pavers_bu")
    m.use_nodes = True
    bs = m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.36, 0.345, 0.32, 1)
    bs.inputs["Roughness"].default_value = 0.82
    return m

Mstep = mat_concrete()
Mrail = mat_rail()
Mmulch = mat_mulch_smooth()
Mpaver = mat_paver(ang)

# ========================================================================
# 1. WEST EDGE STEPS + RAILINGS (toward Kasser drive)
# ========================================================================
# Walkway centreline from plaza west edge westward. y chosen where DTM drop is largest.
# EDGE polyline along west deck (slight outward bulge to match ortho curve — UNVERIFIED form).
Y0, Y1 = -98.0, -78.0  # stair band along plaza west edge
X_EDGE = -199.0
# sample tops along edge
edge_pts = []
for i in range(11):
    t = i / 10.0
    y = Y0 + t * (Y1 - Y0)
    # slight west bulge mid-band (ortho curved tiers) — 0.8 m UNVERIFIED
    bulge = 0.8 * math.sin(math.pi * t)
    x = X_EDGE - bulge
    z = ground_z(X_EDGE, y, prefer_deck=True)
    if z is None:
        z = ground_z(X_EDGE, y)
    if z is None:
        continue
    edge_pts.append(Vector((x, y, z)))
print("EDGE_PTS", len(edge_pts), "z", round(min(p.z for p in edge_pts), 2), round(max(p.z for p in edge_pts), 2))

# drive / bottom level just west of steps run
bottoms = []
for p in edge_pts:
    # Kasser-drive asphalt band west of plaza (MEASURED from DTM probes ~x −220)
    zs = []
    for xw in (-225.0, -220.0, -215.0, -212.0):
        zb = ground_z(xw, p.y)
        if zb is not None:
            zs.append(zb)
    bottoms.append(min(zs) if zs else p.z - 1.5)
top_med = statistics.median([p.z for p in edge_pts])
bot_med = statistics.median(bottoms)
drop = top_med - bot_med
print("STEP_DROP MEASURED top", round(top_med, 2), "bot", round(bot_med, 2), "drop", round(drop, 2))

# Riser plan: target ~0.15–0.18 m (ADA-ish); count from measured drop. Count UNVERIFIED.
RISER = 0.165
NR = max(3, min(12, int(round(drop / RISER))))
H = drop / NR
TREAD = 0.42  # UNVERIFIED (wide plaza terrace tread; ortho shows broad tiers)
print("RISERS", NR, "H", round(H, 3), "TREAD", TREAD, "UNVERIFIED count/tread")

# Outward normal ≈ −X (west). Build mitered strips like SC court steps.
P = [Vector((p.x, p.y)) for p in edge_pts]
# outward = west = (-1, 0) with slight follow of edge tangent
NS = []
for i in range(len(P) - 1):
    t = (P[i + 1] - P[i]).normalized()
    n = Vector((-t.y, t.x))  # left of tangent
    if n.x > 0:  # want west (negative x)
        n = -n
    NS.append(n)
MIT = []
for i in range(len(P)):
    if i == 0:
        MIT.append(NS[0])
    elif i == len(P) - 1:
        MIT.append(NS[-1])
    else:
        m = (NS[i - 1] + NS[i]).normalized()
        MIT.append(m / max(0.45, m.dot(NS[i])))

V, F = [], []
def strip(d0, d1, zt, zb):
    A = [P[i] + MIT[i] * d0 for i in range(len(P))]
    B = [P[i] + MIT[i] * d1 for i in range(len(P))]
    k = len(V); n = len(P)
    for q in A + B:
        V.append((q.x, q.y, zt))
    for q in A + B:
        V.append((q.x, q.y, zb))
    T0, T1, B0, B1 = k, k + n, k + 2 * n, k + 3 * n
    for i in range(n - 1):
        F.append((T0 + i, T1 + i, T1 + i + 1, T0 + i + 1))
        F.append((B0 + i, B0 + i + 1, B1 + i + 1, B1 + i))
        F.append((T1 + i, B1 + i, B1 + i + 1, T1 + i + 1))
        F.append((T0 + i + 1, B0 + i + 1, B0 + i, T0 + i))
    F.append((T0, B0, B1, T1))
    F.append((T1 + n - 1, B1 + n - 1, B0 + n - 1, T0 + n - 1))

# NR treads covering full measured drop
for k in range(NR):
    zt = top_med - (k + 1) * H
    zb = bot_med - 0.35
    strip(k * TREAD, (k + 1) * TREAD, zt, zb)

# landing apron at bottom (thin slab to meet drive)
strip(NR * TREAD, NR * TREAD + 1.2, bot_med + 0.02, bot_med - 0.25)

sm = bpy.data.meshes.new("COLE_plaza_west_steps_bu")
sm.from_pydata(V, [], F)
sm.validate(); sm.update()
sm.materials.append(Mstep)
sob = bpy.data.objects.new("COLE_plaza_west_steps_bu", sm)
link(sob)
sob["bu_note"] = (
    f"west plaza→Kasser-drive steps; LiDAR drop {drop:.2f} m MEASURED (top {top_med:.2f}→bot {bot_med:.2f}); "
    f"{NR} risers × {H:.3f} m, tread {TREAD} m UNVERIFIED; curved edge bulge UNVERIFIED"
)
sob["status"] = "UNVERIFIED"
print("STEPS faces", len(F), "verts", len(V))

# Push terrain under steps so LiDAR facets don't poke through
n_cap = 0
run = NR * TREAD + 1.2
x_west = X_EDGE - run - 1.5
for v in me.vertices:
    if not (x_west - 1.0 < v.co.x < X_EDGE + 0.8 and Y0 - 1.5 < v.co.y < Y1 + 1.5):
        continue
    p = Vector((v.co.x, v.co.y))
    best = None
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]
        tvec = b - a; L = tvec.length
        if L < 1e-6:
            continue
        tvec = tvec / L
        n = MIT[i]
        s = (p - a).dot(tvec)
        d = (p - a).dot(n)
        if -0.8 <= s <= L + 0.8 and -0.5 <= d < run + 0.8:
            best = d
            break
    if best is None:
        continue
    d = best
    if d < 0:
        cap = top_med - 0.06
    elif d >= NR * TREAD:
        cap = bot_med - 0.04
    else:
        k = min(NR - 1, int(d / TREAD))
        cap = top_med - (k + 1) * H - 0.04
    if v.co.z > cap:
        v.co.z = cap
        n_cap += 1
me.update()
print("TERRAIN_CAPPED_UNDER_STEPS", n_cap)

# ---- Railings: two runs along stair sides (north + south ends of edge band) ----
def rail_run(y_side, name):
    """Posts + top + mid rail along outward stair for one cheek."""
    # sample along depth
    pts = []
    for k in range(NR + 2):
        d = min(k * TREAD, NR * TREAD + 0.6)
        # interpolate edge at y_side
        # find x at this y on edge
        x_e = X_EDGE
        for i in range(len(P) - 1):
            if min(P[i].y, P[i + 1].y) - 0.1 <= y_side <= max(P[i].y, P[i + 1].y) + 0.1:
                t = 0 if abs(P[i + 1].y - P[i].y) < 1e-6 else (y_side - P[i].y) / (P[i + 1].y - P[i].y)
                t = max(0, min(1, t))
                x_e = P[i].x + t * (P[i + 1].x - P[i].x)
                n = MIT[i]
                break
        else:
            n = Vector((-1, 0))
        x = x_e + n.x * d
        y = y_side + n.y * d
        if k == 0:
            z = top_med
        elif k >= NR:
            z = bot_med
        else:
            z = top_med - k * H
        pts.append(Vector((x, y, z)))
    # build post+rail mesh
    Rv, Rf = [], []
    post_h = 0.95  # UNVERIFIED
    post_r = 0.025
    rail_r = 0.02
    def add_box(cx, cy, z0, z1, sx, sy):
        k0 = len(Rv)
        for zz in (z0, z1):
            for dy in (-sy, sy):
                for dx in (-sx, sx):
                    Rv.append((cx + dx, cy + dy, zz))
        # 8 verts: 0..3 bottom, 4..7 top
        Rf.extend([
            (k0, k0+1, k0+3, k0+2),
            (k0+4, k0+6, k0+7, k0+5),
            (k0, k0+2, k0+6, k0+4),
            (k0+1, k0+5, k0+7, k0+3),
            (k0, k0+4, k0+5, k0+1),
            (k0+2, k0+3, k0+7, k0+6),
        ])
    for p in pts[::2]:  # every other tread
        add_box(p.x, p.y, p.z, p.z + post_h, post_r, post_r)
    # top + mid rails as thin boxes between consecutive posts
    post_pts = pts[::2]
    for a, b in zip(post_pts, post_pts[1:]):
        mid = (a + b) * 0.5
        dx, dy = b.x - a.x, b.y - a.y
        L = math.hypot(dx, dy) or 1
        # orient thin box along a→b
        hx, hy = dx / L * (L * 0.5), dy / L * (L * 0.5)
        # use axis-aligned approx (good enough for west-ish run)
        for zoff in (post_h - 0.04, post_h * 0.55):
            za = a.z + zoff; zb = b.z + zoff
            z0 = min(za, zb) - rail_r; z1 = max(za, zb) + rail_r
            k0 = len(Rv)
            # elongated along ab
            px, py = -dy / L * rail_r, dx / L * rail_r
            for zz in (z0, z1):
                Rv.append((a.x + px, a.y + py, zz))
                Rv.append((a.x - px, a.y - py, zz))
                Rv.append((b.x - px, b.y - py, zz))
                Rv.append((b.x + px, b.y + py, zz))
            Rf.extend([
                (k0, k0+1, k0+2, k0+3),
                (k0+4, k0+7, k0+6, k0+5),
                (k0, k0+3, k0+7, k0+4),
                (k0+1, k0+5, k0+6, k0+2),
                (k0, k0+4, k0+5, k0+1),
                (k0+3, k0+2, k0+6, k0+7),
            ])
    rm = bpy.data.meshes.new(name)
    rm.from_pydata(Rv, [], Rf)
    rm.validate(); rm.update()
    rm.materials.append(Mrail)
    ro = bpy.data.objects.new(name, rm)
    link(ro)
    ro["bu_note"] = "dark metal stair rail UNVERIFIED height/section; eye-ref Susan_Cole_Hall_.jpg"
    ro["status"] = "UNVERIFIED"
    print("RAIL", name, "verts", len(Rv), "faces", len(Rf))
    return ro

rail_run(Y0 + 0.35, "COLE_plaza_west_rail_S_bu")
rail_run(Y1 - 0.35, "COLE_plaza_west_rail_N_bu")
# centreline rail so eye/closeup cams read the flight (cheek rails alone sit at band ends)
rail_run(-88.0, "COLE_plaza_west_rail_mid_bu")


# ========================================================================
# 2. SMOOTH PLANTING BEDS (replace stair-step terrain mulch)
# ========================================================================
# Outline along Cole north face / beds strip from bs: roughly x −165…−55, y −80…−56
# Build a few bed polygons with Chaikin-smoothed outlines, draped on DTM.

def chaikin(pts, rounds=3):
    pts = [Vector(p) for p in pts]
    for _ in range(rounds):
        out = []
        n = len(pts)
        for i in range(n):
            a = pts[i]; b = pts[(i + 1) % n]
            out.append(a * 0.75 + b * 0.25)
            out.append(a * 0.25 + b * 0.75)
        pts = out
    return pts

# Bed footprints from ortho/drone language (extent UNVERIFIED) — north of Cole, south of walkways
# Split into 3 beds along the north face so outlines stay organic.
beds_raw = [
    # west planting near plaza/portico north
    [(-165, -78), (-145, -78), (-145, -58), (-155, -56), (-165, -58)],
    # mid north face
    [(-145, -78), (-110, -78), (-110, -57), (-130, -55.5), (-145, -58)],
    # east toward addition / morehead side
    [(-110, -78), (-75, -78), (-70, -62), (-75, -56), (-95, -55.5), (-110, -57)],
]

Mv, Mf = [], []
bed_face_ranges = []
for bi, raw in enumerate(beds_raw):
    sm_pts = chaikin(raw, rounds=4)
    # densify and drape
    ring = []
    for i in range(len(sm_pts)):
        a = sm_pts[i]; b = sm_pts[(i + 1) % len(sm_pts)]
        seg = max(1, int(a.xy.length if False else (a - b).length / 0.6))
        # actually length of a-b
        L = (a - b).length
        nseg = max(1, int(L / 0.55))
        for s in range(nseg):
            t = s / nseg
            q = a.lerp(b, t)
            z = ground_z(q.x, q.y)
            if z is None:
                z = 132.0
            ring.append(Vector((q.x, q.y, z + 0.04)))
    # fan triangulate from centroid
    cx = sum(p.x for p in ring) / len(ring)
    cy = sum(p.y for p in ring) / len(ring)
    cz = sum(p.z for p in ring) / len(ring)
    k0 = len(Mv)
    Mv.append((cx, cy, cz + 0.02))
    for p in ring:
        Mv.append((p.x, p.y, p.z))
    f0 = len(Mf)
    n = len(ring)
    for i in range(n):
        Mf.append((k0, k0 + 1 + i, k0 + 1 + ((i + 1) % n)))
    bed_face_ranges.append((f0, len(Mf)))

# also add a slight thickness via solidify-like duplicate down
# (single sheet + solidify modifier is fine and lighter)
mm = bpy.data.meshes.new("COLE_planting_beds_smooth_bu")
mm.from_pydata(Mv, [], Mf)
mm.validate(); mm.update()
mm.materials.append(Mmulch)
mob = bpy.data.objects.new("COLE_planting_beds_smooth_bu", mm)
link(mob)
# solidify for thickness
mod = mob.modifiers.new("solid", "SOLIDIFY")
mod.thickness = 0.08
mod.offset = 1.0
mob["bu_note"] = "smoothed mulch bed outlines (Chaikin); extent UNVERIFIED vs MSU 2020 drone; replaces stair-step terrain mulch lookup"
mob["status"] = "UNVERIFIED"
print("MULCH_SMOOTH faces", len(Mf), "verts", len(Mv))

# Revert terrain mulch faces → lawn so stair-steps disappear under the new mesh
iM = iL = None
for i, s in enumerate(T.material_slots):
    if s.material and s.material.name == "COLE_planting_mulch_bs":
        iM = i
    if s.material and s.material.name == "COLE_lawn_post2020_bs":
        iL = i
n_rev = 0
if iM is not None and iL is not None:
    for p in me.polygons:
        if p.material_index == iM:
            p.material_index = iL
            n_rev += 1
    me.update()
print("MULCH_TERRAIN_REVERTED_TO_LAWN", n_rev)

# ========================================================================
# 3. ADDITION ENTRANCE RED-BAND FORECOURT
# ========================================================================
# North addition footprint y max ≈ −59.5; entrance faces north. Centre ~ (−107.5, −52).
# Semicircle apron opening north; red bands via shared paver mat (axis-aligned shader).
CX, CY = -107.5, -52.0
R_IN, R_OUT = 3.5, 11.0  # UNVERIFIED sizes
NSECTS = 36
# ground plane LSQ on samples in the apron ring
samples = []
for i in range(NSECTS):
    th = math.radians(i * 360.0 / NSECTS)
    for rr in (R_IN, (R_IN + R_OUT) * 0.5, R_OUT):
        x = CX + rr * math.cos(th); y = CY + rr * math.sin(th)
        # only keep the northern half + a bit (entrance side); skip deep into building
        if y < -59.0:  # inside / under addition
            continue
        z = ground_z(x, y)
        if z is not None:
            samples.append((x, y, z))
if len(samples) < 8:
    # fallback flat
    z0 = ground_z(CX, CY) or 133.5
    samples = [(CX + 4, CY + 2, z0), (CX - 4, CY + 2, z0), (CX, CY + 6, z0)]
sx = sum(p[0] for p in samples) / len(samples)
sy = sum(p[1] for p in samples) / len(samples)
sz = sum(p[2] for p in samples) / len(samples)
sxx = sum((p[0] - sx) ** 2 for p in samples)
syy = sum((p[1] - sy) ** 2 for p in samples)
sxy = sum((p[0] - sx) * (p[1] - sy) for p in samples)
sxz = sum((p[0] - sx) * (p[2] - sz) for p in samples)
syz = sum((p[1] - sy) * (p[2] - sz) for p in samples)
det = sxx * syy - sxy * sxy
if abs(det) < 1e-8:
    ga = gb = 0.0
else:
    ga = (sxz * syy - syz * sxy) / det
    gb = (syz * sxx - sxz * sxy) / det
def plane(x, y):
    return sz + ga * (x - sx) + gb * (y - sy) + 0.03

print("FORECOURT_PLANE z0", round(sz, 2), "grad", round(ga, 4), round(gb, 4), "n", len(samples))

# Build annular sector: north-facing 200° arc (open to N), closed against building
# Angles: 0=east, 90=north in standard math if y is north — here +Y is north-ish in scene.
# Scene: +Y ≈ north. Entrance faces +Y. Arc from 10° to 170° (math angle from +X).
A0, A1 = math.radians(5), math.radians(175)
Fv, Ff = [], []
# polar grid
NRR = 8
NTH = 28
idx = {}
for j in range(NRR + 1):
    rr = R_IN + (R_OUT - R_IN) * j / NRR
    for i in range(NTH + 1):
        th = A0 + (A1 - A0) * i / NTH
        x = CX + rr * math.cos(th)
        y = CY + rr * math.sin(th)
        # clip anything south of addition north face deeper than ~1 m into building
        if y < -60.5:
            continue
        z = plane(x, y)
        idx[(j, i)] = len(Fv)
        Fv.append((x, y, z))
for j in range(NRR):
    for i in range(NTH):
        q = [(j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i)]
        if all(k in idx for k in q):
            Ff.append([idx[k] for k in q])

fm = bpy.data.meshes.new("COLE_add_forecourt_bu")
fm.from_pydata(Fv, [], Ff)
fm.validate(); fm.update()
for p in fm.polygons:
    p.use_smooth = True
fm.materials.append(Mpaver)
fob = bpy.data.objects.new("COLE_add_forecourt_bu", fm)
link(fob)
fob["bu_note"] = (
    f"2020 north-addition entrance forecourt; LSQ on LiDAR ground MEASURED; "
    f"curved apron R {R_IN}–{R_OUT} m + red bands on Cole axis {ang:.1f}°; radius/pitch UNVERIFIED "
    f"(spring-2020 ortho still construction)"
)
fob["status"] = "UNVERIFIED"
print("FORECOURT faces", len(Ff), "verts", len(Fv))

# light terrain push under forecourt
n_push = 0
for v in me.vertices:
    dx = v.co.x - CX; dy = v.co.y - CY
    rr = math.hypot(dx, dy)
    if R_IN - 0.5 < rr < R_OUT + 0.5 and v.co.y > -61:
        th = math.atan2(dy, dx)
        if A0 - 0.05 <= th <= A1 + 0.05:
            cap = plane(v.co.x, v.co.y) - 0.06
            if v.co.z > cap:
                v.co.z = cap
                n_push += 1
me.update()
print("TERRAIN_PUSHED_UNDER_FORECOURT", n_push)

# ========================================================================
# 4. CAMERAS
# ========================================================================
def ensure_cam(nm, loc, tgt, lens, ref_nm="CAM_closeup_cole_hall_plaza_bs"):
    o = bpy.data.objects.get(nm)
    if o is None:
        cd = bpy.data.cameras.new(nm)
        o = bpy.data.objects.new(nm, cd)
        ref = bpy.data.objects.get(ref_nm) or bpy.data.objects.get("CAM_oblique_cole_hall_nnw_br")
        if ref and ref.users_collection:
            ref.users_collection[0].objects.link(o)
        else:
            bpy.context.scene.collection.objects.link(o)
        if ref:
            o.data.clip_start = ref.data.clip_start
            o.data.clip_end = ref.data.clip_end
    o.data.lens = lens
    o.location = loc
    dirv = (Vector(tgt) - Vector(loc)).normalized()
    o.rotation_euler = dirv.to_track_quat("-Z", "Y").to_euler()
    print("CAMSET", nm, tuple(round(a, 2) for a in o.location), "lens", lens)
    return o

# 1) oblique plaza + west steps
gz = ground_z(-210, -70) or 128.0
ensure_cam(
    "CAM_oblique_cole_plaza_edge_bu",
    (-210.0, -55.0, gz + 20.0),
    (-190.0, -88.0, gz + 1.5),
    30,
)
# 2) eye from Kasser-drive side looking at steps+plaza
gz2 = ground_z(-222, -90) or 126.5
ensure_cam(
    "CAM_eye_cole_plaza_steps_west_bu",
    (-214.0, -88.0, bot_med + 1.55),
    (-200.0, -88.0, top_med + 0.3),
    32,
)
# 3) eye of addition entrance forecourt
gz3 = ground_z(-107.5, -35) or 134.0
ensure_cam(
    "CAM_eye_cole_add_forecourt_bu",
    (-107.5, -32.0, gz3 + 1.7),
    (-107.5, -58.0, gz3 + 1.5),
    28,
    ref_nm="CAM_eye_cole_hall_north_addition_bq",
)
# 4) close-up steps/railings
gz4 = ground_z(-208, -88) or 127.0
ensure_cam(
    "CAM_closeup_cole_plaza_steps_bu",
    (-205.5, -88.0, bot_med + 0.95),
    (-200.5, -88.0, top_med - 0.4),
    35,
)

# flag
T[FLAG] = json.dumps({
    "tag": "20261016bu",
    "step_drop_m": round(drop, 3),
    "step_top": round(top_med, 3),
    "step_bot": round(bot_med, 3),
    "risers": NR,
    "riser_h": round(H, 4),
    "tread": TREAD,
    "mulch_terrain_reverted": n_rev,
    "forecourt_samples": len(samples),
    "axis_deg": round(ang, 2),
})
print("FLAG", T[FLAG])

if os.environ.get("SAVE") == "1":
    bpy.ops.wm.save_mainfile()
    print("SAVED", bpy.data.filepath)
else:
    print("DRY_RUN (set SAVE=1 to write)")

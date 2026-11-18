"""tag 20261016bs: Cole Hall surroundings ground (idempotent; SAVE=1 to write).
Problem (br self-review): around Cole Hall the terrain shows the spring-2020 NJ ortho (construction dirt during the
2018-20 renovation/addition) through Ground_ortho_grass / Lawn_Varied ortho fallback -> pale sand, plus DTM spikes
(+2-3 m single-vertex non-ground returns) that read as dunes.
Fix from data:
 1. Despike terrain verts in the Cole Hall zone (x -215..-50, y -165..-40): any vert > 0.30 m above/below its 1-ring
    median is set to the median (3 passes), then 2 gentle Laplacian passes (|dz| capped 0.25 m). Overall LiDAR slope kept.
 2. Re-classify terrain polys in the zone from the 2020 ortho pixel under each poly (UV 'ortho'):
    - west plaza box (x -206..-164, y -104..-48) and pale/grey low-saturation ortho -> COLE_plaza_pavers_bs
      (light pavers + red-brick bands on the Cole Hall axis; extent from ortho, band pattern from the MSU 2020 drone
      photo by eye; band spacing/width UNVERIFIED)
    - brown/tan construction dirt or green -> COLE_lawn_post2020_bs (copy of Lawn_Varied_Oct_local_fade with the ortho
      fallback switched off: the Oct 2020 drone photo shows finished lawns there; lawn edges UNVERIFIED)
    - grey/shadow ortho in the strip north of the north wall -> COLE_planting_mulch_bs (planting beds per drone photo)
    - other grey/asphalt-looking ortho (sat < 0.10): unchanged.
Original material index and z stored once in mesh attributes bs_orig_mat / bs_orig_z so reruns start from the original.
"""
import bpy, bmesh, os, json, math, statistics
from mathutils import Vector
TAG = "bs"
T = bpy.data.objects["Terrain_LiDAR_DTM_1m"]; me = T.data
ZONE = (-215.0, -50.0, -165.0, 5.0)   # incl. Alumni Green west part (OSM leisure=park)
PLAZA = (-199.0, -164.0, -100.0, -57.0)  # pale curved plaza in the 2020 ortho + drone photo (edges UNVERIFIED)
here = os.path.dirname(bpy.data.filepath)

# ---------- materials ----------
def lawn_mat():
    m = bpy.data.materials.get("COLE_lawn_post2020_bs")
    if m: return m
    m = bpy.data.materials["Lawn_Varied_Oct_local_fade"].copy(); m.name = "COLE_lawn_post2020_bs"
    nt = m.node_tree; ms = nt.nodes["Mix Shader"]
    for l in list(ms.inputs[0].links): nt.links.remove(l)
    ms.inputs[0].default_value = 1.0   # always the grass shader (no 2020-ortho dirt fallback)
    m["bs_note"] = "Lawn_Varied copy, ortho fallback off; lawn per MSU Oct 2020 drone photo (edges UNVERIFIED)"
    return m

def cole_axis_deg():
    d = json.load(open(os.path.join(here, "data", "scene_data.json")))
    for f in d["features"]:
        if f["id"] == "312932811":
            p = f["pts"]; best = (0, 0)
            for a, b in zip(p, p[1:] + p[:1]):
                L = math.hypot(b[0]-a[0], b[1]-a[1])
                if L > best[0]: best = (L, math.degrees(math.atan2(b[1]-a[1], b[0]-a[0])))
            return best[1]
    return -14.0

def paver_mat(ang):
    m = bpy.data.materials.get("COLE_plaza_pavers_bs")
    if m is None: m = bpy.data.materials.new("COLE_plaza_pavers_bs")
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N = nt.nodes.new; L = nt.links.new
    out = N("ShaderNodeOutputMaterial"); bs = N("ShaderNodeBsdfPrincipled")
    tc = N("ShaderNodeTexCoord"); mp = N("ShaderNodeMapping"); mp.inputs["Rotation"].default_value[2] = -math.radians(ang)
    L(tc.outputs["Object"], mp.inputs["Vector"]); sep = N("ShaderNodeSeparateXYZ"); L(mp.outputs["Vector"], sep.inputs[0])
    def band(sock, period, width):
        a = N("ShaderNodeMath"); a.operation = "FLOORED_MODULO"; a.inputs[1].default_value = period; L(sock, a.inputs[0])
        b = N("ShaderNodeMath"); b.operation = "LESS_THAN"; b.inputs[1].default_value = width; L(a.outputs[0], b.inputs[0])
        return b.outputs[0]
    def mx(a, b):
        n = N("ShaderNodeMath"); n.operation = "MAXIMUM"; L(a, n.inputs[0]); L(b, n.inputs[1]); return n.outputs[0]
    red = mx(band(sep.outputs[0], 6.6, 0.55), band(sep.outputs[1], 6.6, 0.55))       # red brick bands (UNVERIFIED pitch)
    jnt = mx(band(sep.outputs[0], 0.60, 0.012), band(sep.outputs[1], 1.20, 0.012))     # slab joints 0.6 x 1.2 m (UNVERIFIED)
    nz = N("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.9; nz.inputs["Detail"].default_value = 5; L(tc.outputs["Object"], nz.inputs["Vector"])
    nz2 = N("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 7.0; L(tc.outputs["Object"], nz2.inputs["Vector"])
    base = N("ShaderNodeMix"); base.data_type = "RGBA"; L(nz.outputs["Fac"], base.inputs["Factor"])
    base.inputs["A"].default_value = (0.32, 0.305, 0.285, 1); base.inputs["B"].default_value = (0.41, 0.395, 0.37, 1)
    rc = N("ShaderNodeMix"); rc.data_type = "RGBA"; L(red, rc.inputs["Factor"]); L(base.outputs["Result"], rc.inputs["A"])
    rr = N("ShaderNodeMix"); rr.data_type = "RGBA"; L(nz2.outputs["Fac"], rr.inputs["Factor"])
    rr.inputs["A"].default_value = (0.26, 0.075, 0.05, 1); rr.inputs["B"].default_value = (0.34, 0.11, 0.07, 1)
    L(rr.outputs["Result"], rc.inputs["B"])
    jm = N("ShaderNodeMath"); jm.operation = "MULTIPLY_ADD"; L(jnt, jm.inputs[0]); jm.inputs[1].default_value = -0.22; jm.inputs[2].default_value = 1.0
    fin = N("ShaderNodeMix"); fin.data_type = "RGBA"; fin.blend_type = "MULTIPLY"; fin.inputs["Factor"].default_value = 1.0
    L(rc.outputs["Result"], fin.inputs["A"]); cj = N("ShaderNodeCombineColor"); [L(jm.outputs[0], cj.inputs[i]) for i in range(3)]
    L(cj.outputs[0], fin.inputs["B"]); L(fin.outputs["Result"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.82
    bump = N("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.01
    inv = N("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0; L(jnt, inv.inputs[1]); L(inv.outputs[0], bump.inputs["Height"])
    L(bump.outputs["Normal"], bs.inputs["Normal"]); L(bs.outputs[0], out.inputs[0])
    m["bs_note"] = f"pavers + red bands on Cole Hall axis {ang:.1f} deg; extent from 2020 ortho, pattern by eye from MSU 2020 drone photo; pitch UNVERIFIED"
    return m

def mulch_mat():
    m = bpy.data.materials.get("COLE_planting_mulch_bs")
    if m: return m
    m = bpy.data.materials.new("COLE_planting_mulch_bs"); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord"); nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 6
    nz2 = nt.nodes.new("ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 0.6
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.035, 0.022, 0.014, 1); cr.color_ramp.elements[1].color = (0.075, 0.048, 0.03, 1)
    sh = nt.nodes.new("ShaderNodeMix"); sh.data_type = "RGBA"; sh.inputs["B"].default_value = (0.05, 0.075, 0.03, 1)   # low shrubs/groundcover patches
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55; mr.inputs["From Max"].default_value = 0.62
    L = nt.links.new
    L(tc.outputs["Object"], nz.inputs["Vector"]); L(tc.outputs["Object"], nz2.inputs["Vector"]); L(nz.outputs["Fac"], cr.inputs["Fac"])
    L(cr.outputs["Color"], sh.inputs["A"]); L(nz2.outputs["Fac"], mr.inputs["Value"]); L(mr.outputs["Result"], sh.inputs["Factor"])
    L(sh.outputs["Result"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.95
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; L(nz.outputs["Fac"], bp.inputs["Height"]); L(bp.outputs["Normal"], bs.inputs["Normal"])
    m["bs_note"] = "planting beds along Cole Hall north face (MSU 2020 drone photo, eye ref); extent = non-green 2020-ortho strip, UNVERIFIED"
    return m

ang = cole_axis_deg(); print("COLE_AXIS_DEG", round(ang, 2))
MM = mulch_mat()
ML = lawn_mat(); MP = paver_mat(ang)
def slot(m):
    for i, s in enumerate(T.material_slots):
        if s.material == m: return i
    me.materials.append(m); return len(me.materials) - 1
iL = slot(ML); iP = slot(MP); iM = slot(MM)

# ---------- originals (stored once) ----------
nv, npoly = len(me.vertices), len(me.polygons)
if "bs_orig_z" not in me.attributes:
    a = me.attributes.new("bs_orig_z", "FLOAT", "POINT"); a.data.foreach_set("value", [v.co.z for v in me.vertices])
    b = me.attributes.new("bs_orig_mat", "INT", "FACE"); b.data.foreach_set("value", [p.material_index for p in me.polygons])
oz = [0.0]*nv; me.attributes["bs_orig_z"].data.foreach_get("value", oz)
om = [0]*npoly; me.attributes["bs_orig_mat"].data.foreach_get("value", om)
for v, z in zip(me.vertices, oz): v.co.z = z
for p, i in zip(me.polygons, om): p.material_index = i

def inz(x, y, Z): return Z[0] < x < Z[1] and Z[2] < y < Z[3]
# ---------- 1. despike + smooth ----------
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
zone = [v for v in bm.verts if inz(v.co.x, v.co.y, ZONE)]
nspk = 0; maxd = 0.0
for it in range(3):
    new = {}
    for v in zone:
        nb = [e.other_vert(v).co.z for e in v.link_edges]
        if len(nb) < 3: continue
        med = statistics.median(nb); srt = sorted(nb)
        # isolated spike / 1-vertex ridge only (keeps real terrace steps): above all but 2 neighbours (or below)
        if v.co.z - srt[-3] > 0.30 or srt[2] - v.co.z > 0.30: new[v] = med
    for v, z in new.items(): maxd = max(maxd, abs(v.co.z - z)); v.co.z = z
    nspk += len(new)
for it in range(2):
    new = {}
    for v in zone:
        nb = [e.other_vert(v).co.z for e in v.link_edges]
        if len(nb) < 3: continue
        d = 0.5 * (sum(nb)/len(nb) - v.co.z); d = max(-0.25, min(0.25, d))
        # fade near zone edge (5 m) so no step at the boundary
        e = min(v.co.x - ZONE[0], ZONE[1] - v.co.x, v.co.y - ZONE[2], ZONE[3] - v.co.y)
        new[v] = v.co.z + d * max(0.0, min(1.0, e / 5.0))
    for v, z in new.items(): v.co.z = z
bm.to_mesh(me); bm.free()
print("DESPIKE verts_fixed", nspk, "max_dz", round(maxd, 2), "zone_verts", len(zone))

# ---------- 2. material reclassification from the 2020 ortho ----------
img = None
for n in bpy.data.materials["Ground_ortho_grass"].node_tree.nodes:
    if n.type == "TEX_IMAGE" and n.image and "ortho2020" in n.image.filepath: img = n.image
W, H = img.size; px = list(img.pixels)  # RGBA float, row 0 = bottom
uv = me.uv_layers["ortho"].data
cnt = {"paver": 0, "lawn": 0, "mulch": 0, "keep": 0}
BEDS = (-165.0, -55.0, -80.0, -55.0)   # strip north of the Cole Hall north wall (drone photo shows planting beds there)
for p in me.polygons:
    c = p.center
    if not inz(c.x, c.y, ZONE): continue
    u = sum(uv[li].uv.x for li in p.loop_indices)/p.loop_total; w = sum(uv[li].uv.y for li in p.loop_indices)/p.loop_total
    ix = min(W-1, max(0, int(u*W))); iy = min(H-1, max(0, int(w*H)))
    r = g = b = 0.0; k = 0
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2):
            j = 4*(min(H-1, max(0, iy+dy))*W + min(W-1, max(0, ix+dx))); r += px[j]; g += px[j+1]; b += px[j+2]; k += 1
    r /= k; g /= k; b /= k
    mxv = max(r, g, b); sat = (mxv - min(r, g, b)) / max(mxv, 1e-4); gex = g - (r+b)/2
    if inz(c.x, c.y, PLAZA) and not (gex > 0.04 and sat > 0.15):
        p.material_index = iP; cnt["paver"] += 1
    elif (gex > 0.01 and sat > 0.08) or (r > b + 0.03 and sat >= 0.10) or mxv < 0.25:   # green / dirt / ortho shadow
        p.material_index = iL; cnt["lawn"] += 1
    elif inz(c.x, c.y, BEDS):
        p.material_index = iM; cnt["mulch"] += 1
    else:
        cnt["keep"] += 1
me.update()
print("RECLASS", cnt)
# footpath plates inside the plaza -> same pavers (one continuous plaza surface)
FP = bpy.data.objects["Footpaths_OSM"]; fm = FP.data
if "bs_orig_mat" not in fm.attributes:
    a = fm.attributes.new("bs_orig_mat", "INT", "FACE"); a.data.foreach_set("value", [p.material_index for p in fm.polygons])
fo = [0]*len(fm.polygons); fm.attributes["bs_orig_mat"].data.foreach_get("value", fo)
for p, i in zip(fm.polygons, fo): p.material_index = i
jp = None
for i, sl in enumerate(FP.material_slots):
    if sl.material == MP: jp = i
if jp is None: fm.materials.append(MP); jp = len(fm.materials) - 1
nfp = 0; fmw = FP.matrix_world
for p in fm.polygons:
    c = fmw @ p.center
    if inz(c.x, c.y, PLAZA): p.material_index = jp; nfp += 1
fm.update(); cnt["footpath_faces_paver"] = nfp; print("FOOTPATH_PAVER", nfp, "fp_identity", fmw.is_identity if hasattr(fmw,'is_identity') else fmw)
# 3. one continuous paver deck over the plaza (terrain + tilted OSM footpath plates disagree by up to ~1 m there)
from mathutils.bvhtree import BVHTree
dg = bpy.context.evaluated_depsgraph_get()
# OSM footpath plates inside the plaza are tilted drape artefacts: sink them 0.6 m under the deck (orig z stored)
if "bs_orig_z" not in fm.attributes:
    a = fm.attributes.new("bs_orig_z", "FLOAT", "POINT"); a.data.foreach_set("value", [v.co.z for v in fm.vertices])
fz = [0.0]*len(fm.vertices); fm.attributes["bs_orig_z"].data.foreach_get("value", fz)
nsink = 0
for v, z in zip(fm.vertices, fz):
    v.co.z = z
    if inz(v.co.x, v.co.y, (PLAZA[0]+0.3, PLAZA[1]-0.3, PLAZA[2]+0.3, PLAZA[3]-0.3)): v.co.z = z - 0.6; nsink += 1
fm.update(); print("FOOTPATH_SINK verts", nsink)
JO = bpy.data.objects.get("Footpath control + expansion joints (3h)")
if JO:
    jm_ = JO.data
    if "bs_orig_z" not in jm_.attributes:
        a = jm_.attributes.new("bs_orig_z", "FLOAT", "POINT"); a.data.foreach_set("value", [v.co.z for v in jm_.vertices])
    jz = [0.0]*len(jm_.vertices); jm_.attributes["bs_orig_z"].data.foreach_get("value", jz); nj = 0
    for v, z in zip(jm_.vertices, jz):
        v.co.z = z; w = JO.matrix_world @ v.co
        if inz(w.x, w.y, PLAZA): v.co.z = z - 0.6; nj += 1
    jm_.update(); print("JOINTS_SINK verts", nj)
dg = bpy.context.evaluated_depsgraph_get()
trees = [BVHTree.FromObject(T, dg)]   # deck follows the despiked LiDAR ground only
STEP = 0.5
nx = int((PLAZA[1] - PLAZA[0]) / STEP) + 1; ny = int((PLAZA[3] - PLAZA[2]) / STEP) + 1
raw = [[None]*nx for _ in range(ny)]
for j in range(ny):
    for i in range(nx):
        x = PLAZA[0] + i*STEP; y = PLAZA[2] + j*STEP; zs = []
        for tr in trees:
            h = tr.ray_cast(Vector((x, y, 200.0)), Vector((0, 0, -1)))
            if h[0] is not None: zs.append(h[0].z)
        raw[j][i] = max(zs) if zs else None
def g(j, i):
    return raw[min(ny-1, max(0, j))][min(nx-1, max(0, i))]
# least-squares plane through the plaza ground samples (the drone photo shows one gently sloping paved plane)
pts_ = [(PLAZA[0] + i*STEP, PLAZA[2] + j*STEP, raw[j][i]) for j in range(ny) for i in range(nx) if raw[j][i] is not None]
n_ = len(pts_); sx = sum(p[0] for p in pts_)/n_; sy = sum(p[1] for p in pts_)/n_; sz = sum(p[2] for p in pts_)/n_
sxx = sum((p[0]-sx)**2 for p in pts_); syy = sum((p[1]-sy)**2 for p in pts_); sxy = sum((p[0]-sx)*(p[1]-sy) for p in pts_)
sxz = sum((p[0]-sx)*(p[2]-sz) for p in pts_); syz = sum((p[1]-sy)*(p[2]-sz) for p in pts_)
det = sxx*syy - sxy*sxy; ga = (sxz*syy - syz*sxy)/det; gb = (syz*sxx - sxz*sxy)/det
def plane(x, y): return sz + ga*(x - sx) + gb*(y - sy)
print("PLAZA_PLANE z0", round(sz, 2), "grad", round(ga, 4), round(gb, 4))
dn = "COLE_plaza_deck_bs"
old_o = bpy.data.objects.get(dn)
if old_o: bpy.data.meshes.remove(old_o.data)
verts = []; idx = {}
for j in range(ny):
    for i in range(nx):
        if raw[j][i] is None: continue
        nb = [g(j+a, i+b) for a in range(-3, 4) for b in range(-3, 4)]; nb = [z for z in nb if z is not None]
        X = PLAZA[0] + i*STEP; Y = PLAZA[2] + j*STEP; pz = plane(X, Y)
        z = pz + 0.35*(sum(nb)/len(nb) - pz) + 0.04   # plane + 35 % of the 3.5 m LiDAR mean residual; terrain pushed under
        idx[(j, i)] = len(verts); verts.append((X, Y, z))
faces = []
for j in range(ny-1):
    for i in range(nx-1):
        q = [(j, i), (j, i+1), (j+1, i+1), (j+1, i)]
        if all(k in idx for k in q): faces.append([idx[k] for k in q])
# push terrain verts under the deck (deck z - 0.12) so lawn never pokes through; deck stays on the LiDAR mean
def deck_z(x, y):
    fi = (x - PLAZA[0]) / STEP; fj = (y - PLAZA[2]) / STEP
    i0 = int(math.floor(fi)); j0 = int(math.floor(fj)); zs = []
    for (jj, ii) in ((j0, i0), (j0, i0+1), (j0+1, i0), (j0+1, i0+1)):
        if (jj, ii) in idx: zs.append(verts[idx[(jj, ii)]][2])
    return min(zs) if zs else None
npush = 0
for v in me.vertices:
    if inz(v.co.x, v.co.y, (PLAZA[0]+0.6, PLAZA[1]-0.6, PLAZA[2]+0.6, PLAZA[3]-0.6)):
        dz = deck_z(v.co.x, v.co.y)
        if dz is not None and v.co.z > dz - 0.12: v.co.z = dz - 0.12; npush += 1
me.update(); print("TERRAIN_PUSHED_UNDER_DECK", npush)
dm = bpy.data.meshes.new(dn); dm.from_pydata(verts, [], faces); dm.materials.append(MP)
for p in dm.polygons: p.use_smooth = True
do = bpy.data.objects.new(dn, dm)
col = bpy.data.collections.get("COLE_ground_20261016bs")
if col is None:
    col = bpy.data.collections.new("COLE_ground_20261016bs"); bpy.context.scene.collection.children.link(col)
col.objects.link(do)
do["bs_note"] = "paver deck z = despiked LiDAR ground, LSQ plane + 35% of 7x7 (3.5 m) LiDAR mean residual +0.04 m, terrain under it pushed 0.12 m below; old path joint grooves sunk too; OSM footpath plates under it sunk 0.6 m; extent = 2020 ortho pale plaza (UNVERIFIED edges)"
cnt["deck_faces"] = len(faces); print("DECK faces", len(faces))
# 4. edge band (0.3 m, +0.10 m) around the deck so the plaza does not end as a paper-thin sheet on the lawn (UNVERIFIED detail)
cn = "COLE_plaza_edge_bs"; oc = bpy.data.objects.get(cn)
if oc: bpy.data.meshes.remove(oc.data)
cm = bpy.data.materials.get("COLE_plaza_curb_bs")
if cm is None:
    cm = bpy.data.materials.new("COLE_plaza_curb_bs"); cm.use_nodes = True
    b_ = cm.node_tree.nodes["Principled BSDF"]; b_.inputs["Base Color"].default_value = (0.30, 0.295, 0.285, 1); b_.inputs["Roughness"].default_value = 0.85
ev_, ef_ = [], []
def strip(cells, inward):
    for k in range(len(cells) - 1):
        (j0, i0), (j1, i1) = cells[k], cells[k+1]
        if (j0, i0) not in idx or (j1, i1) not in idx: continue
        a0 = Vector(verts[idx[(j0, i0)]]); a1 = Vector(verts[idx[(j1, i1)]]); w = Vector(inward) * 0.30
        base = len(ev_)
        for P in (a0, a1):
            ev_.extend([(P.x, P.y, P.z - 0.15), (P.x, P.y, P.z + 0.10), (P.x + w.x, P.y + w.y, P.z + 0.10), (P.x + w.x, P.y + w.y, P.z - 0.02)])
        ef_.extend([[base+0, base+4, base+5, base+1], [base+1, base+5, base+6, base+2], [base+2, base+6, base+7, base+3]])
strip([(0, i) for i in range(nx)], (0, 1, 0)); strip([(ny-1, i) for i in range(nx)], (0, -1, 0))
strip([(j, 0) for j in range(ny)], (1, 0, 0)); strip([(j, nx-1) for j in range(ny)], (-1, 0, 0))
emesh = bpy.data.meshes.new(cn); emesh.from_pydata(ev_, [], ef_); emesh.materials.append(cm)
eo = bpy.data.objects.new(cn, emesh); col.objects.link(eo); eo["bs_note"] = "plaza edge band 0.3 m x +0.10 m, UNVERIFIED"
print("EDGE faces", len(ef_))
T["bs_cole_plaza_ground"] = json.dumps({"tag": "20261016bs", "despiked": nspk, **cnt, "axis_deg": round(ang, 2)})
if os.environ.get("SAVE") == "1":
    bpy.ops.wm.save_mainfile(); print("SAVED")

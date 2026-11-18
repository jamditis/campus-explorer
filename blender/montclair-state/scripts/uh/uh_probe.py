"""Session uh probe: locate crease / curl / sawtooth leftovers from ug."""
import bpy, json, math
from mathutils import Vector
D = '/workspace/nj-scenes/montclair-state/data/uh/'
dg = bpy.context.evaluated_depsgraph_get()

def caster(n):
    o = bpy.data.objects.get(n)
    if not o: return lambda x,y: (None, None)
    e = o.evaluated_get(dg); mw = o.matrix_world; iw = mw.inverted()
    d = (iw.to_3x3() @ Vector((0, 0, -1))).normalized()
    def f(x, y):
        r = e.ray_cast(iw @ Vector((x, y, 400)), d)
        return ((mw @ r[1]).z, r[3]) if r[0] else (None, None)
    return f

UG = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA = caster('SA_ground_lower_patch_UNVERIFIED')
DT = caster('Terrain_LiDAR_DTM_1m')
out = []

# 1) crease: sample z along y=247.5..252 at several x, compare UG vs SA vs DTM
print('=== CREASE UG vs SA along seam ===')
crease = []
for x in range(-67, -35, 2):
    for y in [247.0, 248.0, 249.0, 250.0, 250.5, 251.0, 251.5, 252.0]:
        ugz,_ = UG(x+0.5, y); saz,_ = SA(x+0.5, y); dtz,_ = DT(x+0.5, y)
        row = dict(x=x+0.5, y=y, ug=ugz, sa=saz, dt=dtz)
        if ugz is not None and saz is not None:
            row['dz'] = ugz - saz
        crease.append(row)
        if ugz is not None or saz is not None:
            print(f'CR x={x+0.5:6.1f} y={y:5.1f} ug={ugz} sa={saz} dt={dtz} dz={row.get("dz")}')

# 2) SA verts near seam edge that may still be low / stepped vs UG
print('=== SA verts near UG boundary ===')
sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
smw = sao.matrix_world
sa_edge = []
for v in sao.data.vertices:
    p = smw @ v.co
    if -68 < p.x < -35 and 249.5 < p.y < 253.5:
        ugz,_ = UG(p.x, p.y)
        sa_edge.append((v.index, p.x, p.y, p.z, ugz, (ugz - p.z) if ugz else None))
sa_edge.sort(key=lambda t: (t[5] is None, -(abs(t[5]) if t[5] else 0)))
print('SA edge verts sample (top 20 by |dz|):')
for t in sa_edge[:20]:
    print('SAE', t)

# 3) UG verts at north edge (y~250.5+) vs SA
print('=== UG verts north edge ===')
ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
umw = ugo.matrix_world
ug_n = []
for v in ugo.data.vertices:
    p = umw @ v.co
    if p.y > 249.5:
        saz,_ = SA(p.x, p.y)
        ug_n.append((v.index, p.x, p.y, p.z, saz, (p.z - saz) if saz else None))
ug_n.sort(key=lambda t: (t[5] is None, -(abs(t[5]) if t[5] else 0)))
for t in ug_n[:25]:
    print('UGN', t)

# 4) curled paving corner near y≈246 — QXP / QY
print('=== QXP/QY paving near y=246 curl ===')
for nm in ('QXP_pedestrian_area_313024781_paving_UNVERIFIED', 'QY_plaza_rim_band_313024781_UNVERIFIED'):
    o = bpy.data.objects.get(nm)
    if not o: print('MISS', nm); continue
    mw = o.matrix_world
    cand = []
    for v in o.data.vertices:
        p = mw @ v.co
        if -70 < p.x < -30 and 243 < p.y < 252:
            # compare to local ground
            gz = None
            for c in (UG, SA, DT):
                gz,_ = c(p.x, p.y)
                if gz is not None: break
            cand.append((v.index, p.x, p.y, p.z, gz, (p.z - gz) if gz else None))
    # find outliers: high dz or high local curvature proxy (neighbors)
    cand.sort(key=lambda t: (t[5] is None, -(t[5] if t[5] else -999)))
    print(nm, 'n=', len(cand), 'highest above ground:')
    for t in cand[:15]:
        print('PAV', nm[:20], t)
    cand2 = sorted(cand, key=lambda t: (t[5] is None, t[5] if t[5] else 999))
    print(nm, 'lowest below/near ground:')
    for t in cand2[:10]:
        print('PAVlo', nm[:20], t)

# 5) W stair sawtooth — objects around door 404 / apron / walks
print('=== W stair / apron objects ===')
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    n = o.name
    if not any(k in n for k in ('404', 'apron', 'Partridge', 'TY_footway_31302640', 'TY Partridge')):
        continue
    mw = o.matrix_world
    xs, ys, zs = [], [], []
    for v in o.data.vertices:
        p = mw @ v.co
        if -110 < p.x < -95 and 240 < p.y < 260:
            xs.append(p.x); ys.append(p.y); zs.append(p.z)
    if xs:
        print(f'WOBJ {n}: n_in_box={len(xs)} x[{min(xs):.2f},{max(xs):.2f}] y[{min(ys):.2f},{max(ys):.2f}] z[{min(zs):.2f},{max(zs):.2f}] verts={len(o.data.vertices)} polys={len(o.data.polygons)}')

# 6) sample apron / walk 404 / steps boundary verts for sawtooth (xy zig-zag of outer edge)
print('=== W apron outer edge sample ===')
for nm in ('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)',
           'TY_footway_313026404_to_Partridge_UNVERIFIED',
           'TY Partridge entrance steps+landings (UNVERIFIED)'):
    o = bpy.data.objects.get(nm)
    if not o: print('MISS', nm); continue
    mw = o.matrix_world
    # find boundary edges
    me = o.data
    edge_use = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            edge_use[ek] = edge_use.get(ek, 0) + 1
    bverts = set()
    for ek, c in edge_use.items():
        if c == 1:
            bverts.add(ek[0]); bverts.add(ek[1])
    # W-side outer: low x, mid y
    bv = []
    for vi in bverts:
        p = mw @ me.vertices[vi].co
        if -110 < p.x < -95 and 245 < p.y < 258:
            bv.append((vi, p.x, p.y, p.z))
    bv.sort(key=lambda t: t[2])  # by y
    print(nm, 'boundary in W box', len(bv))
    # compute successive dx as sawtooth proxy
    if len(bv) > 3:
        dxs = [bv[i+1][1] - bv[i][1] for i in range(len(bv)-1)]
        print('  successive dx along y-sort: min/max/mean', min(dxs), max(dxs), sum(dxs)/len(dxs))
        # print verts with large |dx| jumps
        for i in range(len(bv)-1):
            if abs(dxs[i]) > 0.15:
                print('  JUMP', bv[i], '->', bv[i+1], 'dx', dxs[i])

# grass pattern source check
print('=== grass sources ===')
for n in ('cx_grass_points', 'SB_AnnexWest_lawn_grass_points_UNVERIFIED', 'QV_Richardson_NW_lawn_grass_points_UNVERIFIED',
          'UG_Partridge_E_seam_fill_lawn_UNVERIFIED'):
    o = bpy.data.objects.get(n)
    print(n, '->', 'YES' if o else 'NO', 
          ([m.name for m in o.modifiers] if o else None),
          (len(o.data.vertices) if o and o.type=='MESH' else None))

json.dump({'crease_sample': crease[:40], 'sa_edge_top': [list(t) for t in sa_edge[:30]],
           'ug_n_top': [list(t) for t in ug_n[:30]]}, open(D+'probe1.json','w'), indent=1, default=str)
print('WROTE probe1.json')

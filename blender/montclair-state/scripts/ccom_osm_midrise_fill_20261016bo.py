"""2026-10-16 bo: OSM mid-rise band (15-45 m) for the CCOM lab-window skyline, LOCAL to montclair_state.blend.
Adds one joined mesh `BD_osm_mid_fill_bo` (collection `NJ_NY_osm_mid_bo`) from data/ccom_mid_distance/bo/osm_mid_local_20261016bo.json
(prep: osm_midrise_prep_20261016bo.py; only buildings whose roofs clear the 3DEP terrain horizon from the lab cam).
Footprints MEASURED (OSM, ODbL); heights OSM height tag (MEASURED-ish) or levels*3.2+1 (UNVERIFIED); base = 3DEP 30 m - curvature
drop, buried 3 m. Materials: reuses the bn fill mats (BD_*_bn) + face attr bn_val jitter; mid-rise mix leans stone/brick/light (UNVERIFIED tone).
Run AFTER ccom_lab_skyline_contrast_20261016bm.py and ccom_osm_skyline_fill_20261016bn.py. Idempotent. Env SAVE=1 to save."""
import bpy, json, math, os, zlib, functools, builtins
print = functools.partial(builtins.print, flush=True)
FLAG = os.environ.get('BO_FLAG', 'bo_osm_midrise_fill'); COLN = os.environ.get('BO_COLN', 'NJ_NY_osm_mid_bo'); OBN = os.environ.get('BO_OBN', 'BD_osm_mid_fill_bo')
J = os.environ.get('BO_JSON', '/workspace/nj-scenes/montclair-state/data/ccom_mid_distance/bo/osm_mid_local_20261016bo.json')
# 2nd use (bo2): BO_JSON=.../palisades_local_20261016bo.json BO_COLN=NJ_palisades_lidar_bo BO_OBN=BD_palisades_lidar_fill_bo BO_FLAG=bo_palisades_lidar_fill
R, KR = 6371000.0, 0.13
def drop(d): return d * d / (2 * R) * (1 - KR)
sc = bpy.context.scene
assert bpy.data.collections.get('NJ_NY_osm_fill_bn'), 'run bn fill first'
old = bpy.data.collections.get(COLN)
if old:
    obs = [o for o in bpy.data.objects if any(c.name == COLN for c in o.users_collection)]
    for o in obs:
        me = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COLN); sc.collection.children.link(col)
MN = ['BD_glass_tower_bn', 'BD_stone_tower_bn', 'BD_fill_massing_bn', 'BD_osm_light_bn']
M = [bpy.data.materials.get(n) for n in MN]; assert all(M), MN
D = json.load(open(J))
V, F, MI, VAL = [], [], [], []; cnt = [0, 0, 0, 0]
for it in D['items']:
    P = it['poly']; n = len(P); d = it['dist_m']; z0 = it['gz'] - drop(d) - 3.0; z1 = it['gz'] - drop(d) + it['h']
    mt = (it['mat'] + ' ' + it['colour']).lower(); hsh = zlib.crc32(b'bo' + str(it['id']).encode()) % 100
    if 'glass' in mt: m = 0
    elif any(k in mt for k in ('brick', 'stone', 'concrete', 'masonry', 'limestone', 'red', 'brown')): m = 1
    elif any(k in mt for k in ('white', 'beige', 'cream', 'light')): m = 3
    elif os.environ.get('BO_NOGLASS') == '1': m = 1 if hsh < 50 else (3 if hsh < 80 else 2)   # Palisades rowhouses: no glass (UNVERIFIED mix)
    else: m = 1 if hsh < 45 else (3 if hsh < 70 else (2 if hsh < 93 else 0))
    cnt[m] += 1
    val = 0.78 + 0.37 * (zlib.crc32(b'v' + str(it['id']).encode()) % 1000) / 999.0
    o = len(V)
    V += [(x, y, z0) for x, y in P] + [(x, y, z1) for x, y in P]
    for i in range(n):
        j = (i + 1) % n; F.append((o + i, o + j, o + n + j, o + n + i)); MI.append(m); VAL.append(val)
    F.append(tuple(o + n + i for i in range(n))); MI.append(m); VAL.append(val * 1.06)
me = bpy.data.meshes.new(OBN); me.from_pydata(V, [], F); me.validate(); me.update()
for m in M: me.materials.append(m)
assert len(me.polygons) == len(MI), (len(me.polygons), len(MI))
me.polygons.foreach_set('material_index', MI)
at = me.attributes.new('bn_val', 'FLOAT', 'FACE'); at.data.foreach_set('value', VAL)
for p in me.polygons: p.use_smooth = False
ob = bpy.data.objects.new(OBN, me); col.objects.link(ob)
ob['source'] = D['source']; ob['n_buildings'] = D['n']
ob['MEASURED'] = 'footprints (OSM), heights from OSM height tag, ground 3DEP 30 m, curvature drop, terrain-horizon cull'
ob['UNVERIFIED'] = f"{D['levels_only']} heights from levels*3.2+1 m; material by tag/hash; 3 m burial; building-behind-building occlusion not culled"
sc[FLAG] = f"{D['n']} OSM mid-rise bldgs, {len(me.polygons)} faces, mats glass/stone/fill/light {cnt}"
print('BO FILL', sc[FLAG], 'verts', len(me.vertices))
sun = [o for o in bpy.data.objects if o.type == 'LIGHT' and o.data.type == 'SUN']
print('SOFTLIGHT', [(s.name, round(s.data.energy, 4), round(math.degrees(s.data.angle), 2)) for s in sun], sc.view_settings.look,
      [round(x, 4) for x in [n.inputs[1].default_value for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND']])
if os.environ.get('SAVE') == '1':
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)

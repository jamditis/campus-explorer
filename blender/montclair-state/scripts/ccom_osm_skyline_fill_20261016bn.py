"""2026-10-16 bn: data-backed NYC/Hudson skyline fill for the CCOM lab-window view (LOCAL to montclair_state.blend).
Adds one joined low-poly mesh `BD_osm_tall_fill_bn` (collection `NJ_NY_osm_fill_bn`) of 3,463 OSM buildings
(height>=45 m or levels>=14, bbox 40.695..40.800 N, -74.075..-73.930 E; ODbL (c) OpenStreetMap contributors) from
data/ccom_mid_distance/bn/osm_tall_local_20261016bn.json (prep: osm_skyline_prep_20261016bn.py):
  footprint polygon (MEASURED, OSM), height from OSM `height` (MEASURED-ish, NYC import) or levels*3.6 (UNVERIFIED, 209),
  base z = 3DEP 30 m DEM (MEASURED) - curvature/refraction drop d^2/2R*(1-0.13) (same as the asset), buried 3 m.
  Landmarks already modelled in the asset (within 60 m) skipped. Materials: the bm local BD_*_bm set (glass/stone/fill),
  chosen from building:material when tagged, else a stable hash by height (UNVERIFIED tone).
Also hides (does not delete) the random UNVERIFIED Manhattan silhouette fill copy (bm_src BD_fill_Manhattan_UNVERIFIED) which
this replaces with real footprints. Asset file untouched. Run AFTER ccom_lab_skyline_contrast_20261016bm.py (that script rebuilds
NJ_NY_backdrop_local_bm; rerun this one after it). Idempotent. Env SAVE=1 to save."""
import bpy, json, math, os, zlib, functools, builtins
print = functools.partial(builtins.print, flush=True)
FLAG = 'bn_osm_skyline_fill'; COLN = 'NJ_NY_osm_fill_bn'; OBN = 'BD_osm_tall_fill_bn'
J = '/workspace/nj-scenes/montclair-state/data/ccom_mid_distance/bn/osm_tall_local_20261016bn.json'
R, KR = 6371000.0, 0.13
def drop(d): return d * d / (2 * R) * (1 - KR)
sc = bpy.context.scene
assert bpy.data.collections.get('NJ_NY_backdrop_local_bm'), 'run bm skyline script first'
inst = bpy.data.objects.get('NJ_NY_backdrop_instance'); print('INST MW identity?', inst.matrix_world == inst.matrix_world.Identity(4) if inst else None)
old = bpy.data.collections.get(COLN)
if old:
    for o in list(old.all_objects):
        me = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(old)
col = bpy.data.collections.new(COLN); sc.collection.children.link(col)
SRC = {'BD_glass_tower': 'BD_glass_tower_bm', 'BD_stone_tower': 'BD_stone_tower_bm', 'BD_fill_massing': 'BD_fill_massing_bm', 'BD_osm_light': 'BD_stone_tower_bm'}
# fill-only copies of the bm mats (towers keep bm), lighter mid-rise tones + per-building value jitter (face attr bn_val). UNVERIFIED tone vs Joe photo.
BASE = {'BD_glass_tower': (0.24, 0.29, 0.38), 'BD_stone_tower': (0.56, 0.53, 0.48), 'BD_fill_massing': (0.48, 0.48, 0.49), 'BD_osm_light': (0.70, 0.68, 0.64)}
LIFT = float(os.environ.get('BN_LIFT', '1.0'))
for m in list(bpy.data.materials):
    if m.name.endswith('_bn') and m.name.startswith('BD_') and m.users == 0: bpy.data.materials.remove(m)
M = {}
for k, sname in SRC.items():
    sm = bpy.data.materials.get(sname); assert sm, sname
    nm = bpy.data.materials.get(k + '_bn')
    if nm: bpy.data.materials.remove(nm)
    nm = sm.copy(); nm.name = k + '_bn'; nt = nm.node_tree
    bs = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]; inp = bs.inputs['Base Color']
    rgb = tuple(min(1.0, c * LIFT) for c in BASE[k])
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_name = 'bn_val'; at.attribute_type = 'GEOMETRY'
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    if inp.is_linked:   # bm chain: find the RGB node feeding the sun split and set its colour; then multiply the whole chain
        lk = inp.links[0]; src_sock = lk.from_socket
        rn = nt.nodes.get('bm_base')
        if rn: rn.outputs[0].default_value = (*rgb, 1)
        nt.links.remove(lk); nt.links.new(src_sock, mul.inputs['A'])
    else:
        mul.inputs['A'].default_value = (*rgb, 1)
    nt.links.new(at.outputs['Fac'], mul.inputs['B']); nt.links.new(mul.outputs['Result'], inp)
    nm['bn_fill_mat'] = f'copy of {sname}; base {rgb}; x bn_val (0.80..1.15 per building, UNVERIFIED)'
    M[k] = nm
print('BN MATS', {k: v.name for k, v in M.items()}, 'linked base chain', [v.node_tree.nodes[[n.name for n in v.node_tree.nodes if n.type=="BSDF_PRINCIPLED"][0]].inputs['Base Color'].is_linked for v in M.values()])
D = json.load(open(J))
V, F, MI, VAL = [], [], [], []
cnt = {0: 0, 1: 0, 2: 0}
for it in D['items']:
    P = it['poly']; n = len(P); d = it['dist_m']; z0 = it['gz'] - drop(d) - 3.0; z1 = it['gz'] - drop(d) + it['h']
    mt = it['mat'].lower(); hsh = zlib.crc32(str(it['id']).encode()) % 100
    if 'glass' in mt: m = 0
    elif any(k in mt for k in ('brick', 'stone', 'concrete', 'masonry', 'limestone')): m = 1
    elif it['h'] >= 150: m = 0 if hsh < 55 else (1 if hsh < 85 else 3)
    else: m = 3 if hsh < 45 else (1 if hsh < 75 else (2 if hsh < 90 else 0))
    cnt[m] = cnt.get(m, 0) + 1
    val = 0.80 + 0.35 * (zlib.crc32(b'v' + str(it['id']).encode()) % 1000) / 999.0
    o = len(V)
    V += [(x, y, z0) for x, y in P] + [(x, y, z1) for x, y in P]
    for i in range(n):
        j = (i + 1) % n; F.append((o + i, o + j, o + n + j, o + n + i)); MI.append(m); VAL.append(val)
    F.append(tuple(o + n + i for i in range(n))); MI.append(m); VAL.append(val)
me = bpy.data.meshes.new(OBN); me.from_pydata(V, [], F); me.validate(); me.update()
for k in ('BD_glass_tower', 'BD_stone_tower', 'BD_fill_massing', 'BD_osm_light'): me.materials.append(M[k])
assert len(me.polygons) == len(MI), (len(me.polygons), len(MI))
me.polygons.foreach_set('material_index', MI)
at = me.attributes.new('bn_val', 'FLOAT', 'FACE'); at.data.foreach_set('value', VAL)
for p in me.polygons: p.use_smooth = False
ob = bpy.data.objects.new(OBN, me); col.objects.link(ob)
ob['source'] = D['source']; ob['n_buildings'] = D['n']
ob['MEASURED'] = 'footprints (OSM), heights from OSM height tag (NYC import), ground 3DEP 30 m, curvature drop'
ob['UNVERIFIED'] = f"{D['levels_only']} heights from levels*3.6 m; material choice by hash; 3 m burial"
ob.visible_shadow = True
# hide random UNVERIFIED Manhattan fill copy (replaced by real footprints)
hid = []
for o in bpy.data.objects:   # (iterating collection.all_objects after removing a collection segfaulted in 4.5)
    if o.library is None and str(o.get('bm_src', '')).startswith('BD_fill_Manhattan') and any(c.name == 'NJ_NY_backdrop_local_bm' for c in o.users_collection):
        o.hide_render = True; o.hide_viewport = True; o['bn_hidden_by'] = 'ccom_osm_skyline_fill_20261016bn (replaced by OSM footprints)'; hid.append(o.name)
sc[FLAG] = f"{D['n']} OSM bldgs, {len(me.polygons)} faces, mats glass/stone/fill/light {cnt}; hid {hid}"
print('BN FILL', sc[FLAG], 'verts', len(me.vertices))
sun = [o for o in bpy.data.objects if o.type == 'LIGHT' and o.data.type == 'SUN']
print('SOFTLIGHT', [(s.name, round(s.data.energy, 4), round(math.degrees(s.data.angle), 2)) for s in sun], sc.view_settings.look,
      [round(x, 4) for x in [n.inputs[1].default_value for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND']])
if os.environ.get('SAVE') == '1':
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)

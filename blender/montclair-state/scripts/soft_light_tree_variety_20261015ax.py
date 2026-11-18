"""2026-10-15 ax: Joe's Oct 15 note — lighting too harsh -> softer; trees need more variety (species, shape, size, colour).
Works on main montclair_state.blend and north/montclair_north.blend. Deterministic (hash of object name).
Args after --: [--save] [--cam]   (--cam adds CAM_closeup_trees_variety_ax on main / north)
- Sun: angle 0.53 deg -> 3.5 deg (softer shadow edges), energy x0.82; world background strengths x1.3 (shadow fill).
- View look: AgX - Medium High Contrast -> AgX - Base Contrast.
- Trees (Tree_*_LOD1_v2Oct instances): ~11% -> Eastern White Pine, ~8% -> Honey Locust (meshes linked from assets/campus_assets.blend),
  re-scaled so the world height matches the LiDAR-fit height. Non-uniform crown width jitter, small z jitter, random yaw, 0-2.5 deg lean.
  'autumn' per-object attr spread per species (mid-October NJ). Species assignment is UNVERIFIED (LiDAR gives no species).
"""
import bpy, sys, hashlib, math, os
from mathutils import Vector, Euler
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAVE = '--save' in argv; CAM = '--cam' in argv
ASSET = '/workspace/nj-scenes/assets/campus_assets.blend'
TAG = '20261015ax'
sc = bpy.context.scene

def h(name, salt):
    return int(hashlib.md5((name + salt).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

# ---- lighting
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN' and not o.get('ax_soft'):
        o.data.angle = math.radians(3.5); o.data.energy *= 0.82; o['ax_soft'] = 1
        print('SUN', o.name, round(o.data.energy, 3), round(math.degrees(o.data.angle), 2))
w = sc.world
if w and w.use_nodes and not w.get('ax_soft'):
    for n in w.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeBackground':
            n.inputs['Strength'].default_value *= 1.3; print('WORLD', n.name, round(n.inputs['Strength'].default_value, 3))
    w['ax_soft'] = 1
sc.view_settings.look = 'AgX - Base Contrast'
print('LOOK', sc.view_settings.look)

# ---- new species meshes
need = {'Tree_WhitePine_LOD1', 'Tree_HoneyLocust_LOD1'}
have = {m.name for m in bpy.data.meshes if m.library and m.name in need}
if need - have:
    with bpy.data.libraries.load(ASSET, link=True) as (df, dt):
        dt.meshes = [n for n in df.meshes if n in (need - have)]
mesh = {m.name: m for m in bpy.data.meshes if m.name in need and m.library}
def mh(me):
    zs = [v.co.z for v in me.vertices]; return (max(zs) - min(zs)) if zs else 1.0
H = {k: mh(v) for k, v in mesh.items()}
print('NEWMESH', {k: round(v, 2) for k, v in H.items()}, {k: [m.name for m in v.materials if m] for k, v in mesh.items()})

AUT = {  # (lo, hi) autumn attr range per species, mid-Oct northern NJ (UNVERIFIED artistic)
    'RedMaple': (0.02, 0.95), 'SugarMaple': (0.05, 0.80), 'PinOak': (0.0, 0.50), 'LondonPlane': (0.05, 0.55), 'HoneyLocust': (0.15, 0.85)}
stats = {}
trees = [o for o in bpy.data.objects if o.type == 'MESH' and o.data and o.data.name.startswith('Tree_') and '_LOD1_v2Oct' in o.data.name]
for o in trees:
    if o.get('ax_var'): continue
    src = o.data.name.split('_')[1]
    old_h = mh(o.data) * o.scale.z
    r = h(o.name, 'sp')
    sp = src
    if r < 0.11 and old_h > 7.0 and 'Pine' in str(mesh.keys()):
        sp = 'WhitePine'
    elif r < 0.19 and 'Tree_HoneyLocust_LOD1' in mesh:
        sp = 'HoneyLocust'
    if sp in ('WhitePine', 'HoneyLocust'):
        me = mesh['Tree_%s_LOD1' % sp]; s = old_h / max(H['Tree_%s_LOD1' % sp], 0.1)
        o['ax_src_mesh'] = o.data.name; o.data = me; o.scale = (s, s, s)
    # shape / size jitter
    sx = 0.84 + 0.34 * h(o.name, 'sx'); sy = 0.84 + 0.34 * h(o.name, 'sy'); sz = 0.94 + 0.12 * h(o.name, 'sz')
    if sp == 'WhitePine': sx = sy = 0.85 + 0.25 * h(o.name, 'sx')
    o.scale = (o.scale.x * sx, o.scale.y * sy, o.scale.z * sz)
    lean = math.radians(2.5 * h(o.name, 'lean')); la = 2 * math.pi * h(o.name, 'lea')
    o.rotation_euler = Euler((lean * math.cos(la), lean * math.sin(la), 2 * math.pi * h(o.name, 'yaw')), 'XYZ')
    if sp in AUT:
        lo, hi = AUT[sp]; u = h(o.name, 'aut')
        o['autumn'] = lo + (hi - lo) * (u ** 0.85)
    o['ax_var'] = 1; o['ax_species'] = sp
    stats[sp] = stats.get(sp, 0) + 1
print('TREES', len(trees), stats)

# mid-distance street ico crowns: width/height jitter (colour stays objinfo-random)
n = 0
for o in bpy.data.objects:
    if o.name.startswith('MID_stree_20261015ag_') and not o.get('ax_var'):
        o.scale = (o.scale.x * (0.82 + 0.36 * h(o.name, 'sx')), o.scale.y * (0.82 + 0.36 * h(o.name, 'sy')), o.scale.z * (0.85 + 0.3 * h(o.name, 'sz')))
        o.rotation_euler.z = 2 * math.pi * h(o.name, 'yaw'); o['ax_var'] = 1; n += 1
print('MID_STREET_CROWNS', n)

if CAM:
    # closeup on the densest cluster of asset trees, from an unobstructed eye-level spot
    pts = [o for o in trees if o.get('ax_var')]
    best, bc = None, -1
    for i, o in enumerate(pts[::3]):
        c = sum(1 for p in pts if (p.location.xy - o.location.xy).length < 25)
        if c > bc and any(p.get('ax_species') in ('WhitePine', 'HoneyLocust') for p in pts if (p.location.xy - o.location.xy).length < 25): best, bc = o, c
    dg = bpy.context.evaluated_depsgraph_get()
    tgt = best.location + Vector((0, 0, 5.0)); camloc = None
    for k in range(16):
        a = 2 * math.pi * k / 16
        for d in (34, 30, 40):
            L = best.location + Vector((d * math.cos(a), d * math.sin(a), 0))
            hit, loc, *_ = sc.ray_cast(dg, L + Vector((0, 0, 300)), Vector((0, 0, -1)))
            if not hit: continue
            if (L.z if False else loc.z) > best.location.z + 4: continue
            L = Vector((L.x, L.y, loc.z + 1.7))
            hit2, loc2, *_ = sc.ray_cast(dg, L, (tgt - L).normalized(), distance=(tgt - L).length - 12)
            if not hit2: camloc = L; break
        if camloc: break
    if camloc is None: camloc = best.location + Vector((30, 0, 1.7))
    nm = 'CAM_closeup_trees_variety_ax'
    cd = bpy.data.cameras.get(nm) or bpy.data.cameras.new(nm); cd.lens = 35; cd.clip_end = 30000
    co = bpy.data.objects.get(nm) or bpy.data.objects.new(nm, cd)
    if co.name not in sc.collection.objects: sc.collection.objects.link(co)
    co.location = camloc; co.rotation_euler = (tgt - camloc).to_track_quat('-Z', 'Y').to_euler()
    print('CAM', nm, tuple(round(v, 1) for v in camloc), 'cluster', best.name, bc)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)

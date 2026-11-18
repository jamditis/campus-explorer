"""2026-10-15 bb: swap modest fraction of original foursome to Tulip Poplar (both blends).

Species UNVERIFIED; xy + crown-top LiDAR height ACCURATE (from data/bb/tree_z_pre_bb_*.json).
Never swaps WhitePine / HoneyLocust / NorwaySpruce / Sweetgum.
Prefer taller trees (top >10 m). Target ~3–7% of asset trees.

Idempotent via o['bb_tulip']=1 and absolute JSON values.
Args after --: [--save] [--dump-only]  (dump-only writes JSON from current blend then exits)
"""
import bpy, sys, hashlib, math, json, os
from mathutils import Euler

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAVE = '--save' in argv
DUMP_ONLY = '--dump-only' in argv
ASSET = '/workspace/nj-scenes/assets/campus_assets.blend'
which = 'north' if 'north' in os.path.basename(bpy.data.filepath) else 'main'
OUTDIR = '/workspace/nj-scenes/montclair-state/data/bb'
os.makedirs(OUTDIR, exist_ok=True)
JSON_PATH = f'{OUTDIR}/tree_z_pre_bb_{which}.json'

ORIG = ('RedMaple', 'SugarMaple', 'PinOak', 'LondonPlane')
PROTECTED = ('WhitePine', 'HoneyLocust', 'NorwaySpruce', 'Sweetgum', 'TulipPoplar')

def h(name, salt):
    return int(hashlib.md5((name + salt).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

def dump_pre():
    """Dump current asset-tree z/scale/mesh for idempotent absolute restore."""
    data = {}
    for o in bpy.data.objects:
        if not o.get('ax_species') and not (o.data and o.data.name.startswith('Tree_')):
            continue
        if o.type != 'MESH':
            continue
        # campus asset trees from measured_trees / ax / az
        if not (o.name.startswith('MID_lod1_') or o.name.startswith('N_lod1_') or o.name.startswith('T_')
                or o.get('ax_species') or o.get('az_var')):
            # also catch north naming
            if not (o.data and 'Tree_' in (o.data.name or '') and o.get('ax_species')):
                continue
        me = o.data
        if me is None:
            continue
        zs = [v.co.z for v in me.vertices]
        if not zs:
            continue
        zmin, zmax = min(zs), max(zs)
        # scale.z is height scale
        sz = o.scale.z
        data[o.name] = [o.location.z, sz, zmax, zmin, me.name]
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f)
    print('DUMPED', JSON_PATH, len(data))
    return data

if DUMP_ONLY:
    dump_pre()
    # no save
    raise SystemExit(0)

if not os.path.exists(JSON_PATH):
    print('NO_JSON — dumping now from current state before swap')
    PRE = dump_pre()
else:
    PRE = json.load(open(JSON_PATH))
    print('LOADED', JSON_PATH, len(PRE))

need = {'Tree_TulipPoplar_LOD1'}
have = {m.name for m in bpy.data.meshes if m.library and m.name in need}
# also accept local
have |= {m.name for m in bpy.data.meshes if not m.library and m.name in need}
if need - have:
    with bpy.data.libraries.load(ASSET, link=True) as (df, dt):
        dt.meshes = [n for n in df.meshes if n in (need - have)]
mesh = {m.name: m for m in bpy.data.meshes if m.name in need}
if not mesh:
    print('ERROR no TulipPoplar mesh linked'); raise SystemExit(1)

def zr(me):
    zs = [v.co.z for v in me.vertices]
    return (min(zs), max(zs)) if zs else (0.0, 1.0)

Z = {k: zr(v) for k, v in mesh.items()}
print('NEWMESH', which, {k: (round(a, 2), round(b, 2), len(mesh[k].polygons)) for k, (a, b) in Z.items()})

# Fraction: main ~5% of all trees that are still ORIG and top>10m
# Hash gate: bb_tp < 0.055 and top>10 → tulip (≈5.5% of ORIG tall pool)
AUT = (0.20, 0.95)  # yellow→gold autumn spread
stats = {}
moved = 0
skipped_prot = 0
for name, (lz, sz, zmax, zmin, mname) in PRE.items():
    o = bpy.data.objects.get(name)
    if o is None:
        continue
    cur = o.get('ax_species')
    # Restore wrongly stolen protected trees (bb ran using az_src_species bug)
    PROT_MESH = {
        'Tree_WhitePine_LOD1': 'WhitePine',
        'Tree_HoneyLocust_LOD1': 'HoneyLocust',
        'Tree_NorwaySpruce_LOD1': 'NorwaySpruce',
        'Tree_Sweetgum_LOD1': 'Sweetgum',
    }
    if o.get('bb_tulip') and mname in PROT_MESH:
        # PRE mesh was already protected — restore mesh/scale/z from PRE
        # link protected mesh if needed
        need_m = mname
        have_m = next((m for m in bpy.data.meshes if m.name == need_m), None)
        if have_m is None:
            with bpy.data.libraries.load(ASSET, link=True) as (df, dt):
                if need_m in df.meshes:
                    dt.meshes = [need_m]
            have_m = next((m for m in bpy.data.meshes if m.name == need_m), None)
        if have_m:
            o.data = have_m
            o.scale = (sz, sz, sz)  # PRE sz was uniform-ish; keep PRE z scale as z
            # better: restore pre scale from dimensions — PRE stored sz as scale.z
            # width was jittered; use sz for all axes as approx restore
            o.location.z = lz
            o['ax_species'] = PROT_MESH[mname]
            if 'bb_tulip' in o: del o['bb_tulip']
            if 'bb_src_species' in o: del o['bb_src_species']
            if 'bb_src_mesh' in o: del o['bb_src_mesh']
            print('RESTORED', name, PROT_MESH[mname])
            stats[PROT_MESH[mname]] = stats.get(PROT_MESH[mname], 0) + 1
            continue
    # Legitimate existing tulip (PRE mesh was ORIG) — re-anchor to fixed mesh
    if o.get('bb_tulip') and cur == 'TulipPoplar' and mname not in PROT_MESH:
        me = mesh['Tree_TulipPoplar_LOD1']; a, b = Z[me.name]
        top_h = zmax * sz
        s = top_h / max(b, 0.1)
        sx = 0.86 + 0.22 * h(name, 'bb_sx'); sy = 0.86 + 0.22 * h(name, 'bb_sy')
        lean = math.radians(2.0 * h(name, 'bb_lean'))
        la = 2 * math.pi * h(name, 'bb_lea'); yaw = o.rotation_euler.z
        o.data = me; o.scale = (s * sx, s * sy, s); o.location.z = lz
        o.rotation_euler = Euler((lean * math.cos(la), lean * math.sin(la), yaw), 'XYZ')
        stats['TulipPoplar'] = stats.get('TulipPoplar', 0) + 1
        continue
    # Only swap trees that are STILL original foursome (current ax_species)
    new = None
    if cur in ORIG:
        top_h = zmax * sz
        r = h(name, 'bb_tp')
        if r < 0.090 and top_h > 10.0:
            new = 'TulipPoplar'
        elif r < 0.110 and top_h > 12.0:
            new = 'TulipPoplar'
    elif cur in PROTECTED:
        skipped_prot += 1
    if new:
        me = mesh['Tree_%s_LOD1' % new]
        a, b = Z[me.name]
        top_h = zmax * sz
        s = top_h / max(b, 0.1)
        sx = 0.86 + 0.22 * h(name, 'bb_sx')
        sy = 0.86 + 0.22 * h(name, 'bb_sy')
        lean = math.radians(2.0 * h(name, 'bb_lean'))
        la = 2 * math.pi * h(name, 'bb_lea')
        yaw = o.rotation_euler.z
        if not o.get('bb_src_mesh'):
            o['bb_src_mesh'] = mname
        if not o.get('bb_src_species'):
            o['bb_src_species'] = cur
        o.data = me
        o.scale = (s * sx, s * sy, s)
        o.location.z = lz
        o.rotation_euler = Euler((lean * math.cos(la), lean * math.sin(la), yaw), 'XYZ')
        lo, hi = AUT
        o['autumn'] = lo + (hi - lo) * (h(name, 'bb_aut') ** 0.85)
        o['ax_species'] = new
        o['bb_tulip'] = 1
        moved += 1
    sp = o.get('ax_species') or 'unknown'
    stats[sp] = stats.get(sp, 0) + 1

print('TREES', which, len(PRE), 'swapped', moved, 'prot_skip_seen', skipped_prot, stats)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)

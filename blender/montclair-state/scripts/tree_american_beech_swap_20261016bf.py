"""2026-10-16 bf: swap ~3.5% of remaining original-four trees to American Beech LOD1.

Eligible: RedMaple / SugarMaple / PinOak / LondonPlane only.
NEVER: WhitePine / HoneyLocust / NorwaySpruce / Sweetgum / TulipPoplar (or already-beech).

Keeps xy; rescales so crown TOP stays at pre-swap LiDAR-fit top (world z of mesh zmax).
Trunk base (location.z) kept. Species UNVERIFIED.
Idempotent via o['bf_beech']=1.
Args: [--save]
"""
import bpy, sys, hashlib, math, os
from mathutils import Euler
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAVE = '--save' in argv
ASSET = '/workspace/nj-scenes/assets/campus_assets.blend'
which = 'north' if 'north' in os.path.basename(bpy.data.filepath) else 'main'
ORIG = {'RedMaple', 'SugarMaple', 'PinOak', 'LondonPlane'}
BLOCK = {'WhitePine', 'HoneyLocust', 'NorwaySpruce', 'Sweetgum', 'TulipPoplar', 'AmericanBeech'}

def h(name, salt):
    return int(hashlib.md5((name + salt).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

def species_of(o):
    sp = o.get('ax_species') or o.get('az_src_species')
    if sp: return sp
    mn = (o.data.name if o.data else '') or ''
    for k in list(ORIG) + list(BLOCK):
        if k in mn: return k
    return 'unknown'

need = {'Tree_AmericanBeech_LOD1'}
have = {m.name for m in bpy.data.meshes if m.library and m.name in need}
# also accept local (shouldn't be)
have |= {m.name for m in bpy.data.meshes if not m.library and m.name in need}
if need - have:
    with bpy.data.libraries.load(ASSET, link=True) as (df, dt):
        dt.meshes = [n for n in df.meshes if n in (need - have)]
mesh = {m.name: m for m in bpy.data.meshes if m.name in need}
if 'Tree_AmericanBeech_LOD1' not in mesh:
    print('MISSING_BEECH_MESH'); raise SystemExit(1)
me = mesh['Tree_AmericanBeech_LOD1']
zs = [v.co.z for v in me.vertices]
zmin_n, zmax_n = min(zs), max(zs)
print('BEECH_MESH', which, 'z', round(zmin_n, 2), round(zmax_n, 2), 'faces', len(me.polygons),
      'lib', me.library.filepath if me.library else 'local')

eligible = []; skipped = {}
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.data: continue
    if not o.name.startswith('Tree_') and 'tree' not in o.name.lower():
        # campus trees are often Tree_#### or similar — also check mesh
        if not any(k in (o.data.name or '') for k in list(ORIG) + list(BLOCK) + ['Maple', 'Oak', 'Plane', 'Pine', 'Locust', 'Spruce', 'Sweetgum', 'Tulip', 'Beech']):
            continue
    sp = species_of(o)
    if o.get('bf_beech'):
        skipped['already_bf'] = skipped.get('already_bf', 0) + 1
        continue
    if sp in BLOCK:
        skipped[sp] = skipped.get(sp, 0) + 1
        continue
    if sp not in ORIG:
        skipped['other_' + sp] = skipped.get('other_' + sp, 0) + 1
        continue
    # current crown top / base from live mesh
    zs0 = [v.co.z for v in o.data.vertices]
    if not zs0: continue
    zmin0, zmax0 = min(zs0), max(zs0)
    sz = o.scale.z
    top_h = zmax0 * sz  # relative to object origin
    if top_h < 4.0:  # skip shrubs
        skipped['too_short'] = skipped.get('too_short', 0) + 1
        continue
    eligible.append((o, sp, top_h, zmin0, zmax0))

# select ~3.5% of *all* trees that are still original-four — of eligible pool take those with hash < 0.035 / fraction
# Task: ~3-4% of original-four-species trees
moved = 0; stats = {}
for o, sp, top_h, zmin0, zmax0 in eligible:
    r = h(o.name, 'bf_beech')
    if r >= 0.035:
        continue
    s = top_h / max(zmax_n, 0.1)
    sx = 0.86 + 0.28 * h(o.name, 'bf_sx')
    sy = 0.86 + 0.28 * h(o.name, 'bf_sy')
    lean = math.radians(2.0 * h(o.name, 'bf_lean'))
    la = 2 * math.pi * h(o.name, 'bf_lea')
    yaw = o.rotation_euler.z
    if not o.get('bf_src_mesh'):
        o['bf_src_mesh'] = o.data.name
    if not o.get('bf_src_species'):
        o['bf_src_species'] = sp
    o.data = me
    o.scale = (s * sx, s * sy, s)
    # keep location.z (trunk base / origin) — LiDAR xy+height via top match
    o.rotation_euler = Euler((lean * math.cos(la), lean * math.sin(la), yaw), 'XYZ')
    o['autumn'] = 0.25 + 0.70 * (h(o.name, 'bf_aut') ** 0.85)
    o['ax_species'] = 'AmericanBeech'
    o['bf_beech'] = 1
    o['bf_note'] = 'UNVERIFIED species; LiDAR xy+crown-top height kept'
    moved += 1
    stats[sp] = stats.get(sp, 0) + 1

# checksum-ish: sum loc+scale+rot for beech + for tulips (should be unchanged for tulips)
def tulip_chk():
    s = 0.0; n = 0
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.data and 'TulipPoplar' in o.data.name:
            s += sum(o.location) + sum(o.scale) + sum(o.rotation_euler); n += 1
    return n, round(s, 4)

print('ELIGIBLE', which, len(eligible), 'MOVED', moved, 'from', stats, 'skipped', skipped)
print('TULIP_CHK', tulip_chk())
# count beech now
nb = sum(1 for o in bpy.data.objects if o.get('bf_beech'))
print('BEECH_COUNT', nb)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)

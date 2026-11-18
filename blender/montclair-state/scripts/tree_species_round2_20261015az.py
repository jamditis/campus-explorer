"""2026-10-15 az: tree variety round 2 (Joe's Oct 15 direction). Swaps ~7% of the asset trees (original four species only,
never the ax WhitePine/HoneyLocust picks) to two new species linked from assets/campus_assets.blend:
  - Norway Spruce (Tree_NorwaySpruce_LOD1): ~3.5% of trees taller than 8 m.
  - Sweetgum (Tree_Sweetgum_LOD1): ~3.5%.
Tree xy kept; trunk base stays on the pre-az ground contact and the crown TOP stays at the pre-az LiDAR-fit top (LiDAR ACCURATE).
Species per tree UNVERIFIED (LiDAR has no species). Crown jitter like ax (deciduous width x/y 0.84-1.18; spruce uniform 0.88-1.08,
lean <=1 deg); yaw kept from ax. Per-species autumn: Sweetgum 0.10-1.00 (gold->red->purple), Spruce 0.0-0.35.
Also fixes the ax White Pines: Tree_WhitePine_LOD1 has no geometry below z=+3.53 (trunk foot lost in LOD), so ax pines floated
~3.5*s m above ground; they are dropped by zmin*scale so the lowest geometry meets the ground (world height = LiDAR height, unchanged).
Source of truth = data/az/tree_z_pre_az_<main|north>.json (dumped from the *_pre_20261015az.blend backups), so the script sets absolute
values and is idempotent. Args after --: [--save]"""
import bpy, sys, hashlib, math, json, os
from mathutils import Euler
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAVE = '--save' in argv
ASSET = '/workspace/nj-scenes/assets/campus_assets.blend'
which = 'north' if 'north' in os.path.basename(bpy.data.filepath) else 'main'
PRE = json.load(open(f'/workspace/nj-scenes/montclair-state/data/az/tree_z_pre_az_{which}.json'))
def h(name, salt):
    return int(hashlib.md5((name + salt).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
need = {'Tree_NorwaySpruce_LOD1', 'Tree_Sweetgum_LOD1'}
have = {m.name for m in bpy.data.meshes if m.library and m.name in need}
if need - have:
    with bpy.data.libraries.load(ASSET, link=True) as (df, dt):
        dt.meshes = [n for n in df.meshes if n in (need - have)]
mesh = {m.name: m for m in bpy.data.meshes if m.name in need and m.library}
def zr(me):
    zs = [v.co.z for v in me.vertices]; return (min(zs), max(zs)) if zs else (0.0, 1.0)
Z = {k: zr(v) for k, v in mesh.items()}
print('NEWMESH', which, {k: (round(a, 2), round(b, 2), len(mesh[k].polygons)) for k, (a, b) in Z.items()})
AUT = {'Sweetgum': (0.10, 1.00), 'NorwaySpruce': (0.0, 0.35)}
stats = {}; moved = 0; pine = 0
for name, (lz, sz, zmax, zmin, mname) in PRE.items():
    o = bpy.data.objects.get(name)
    if o is None: continue
    sp0 = o.get('az_src_species') or o.get('ax_species')
    if o.get('az_src_species') is None and o.get('ax_species') in ('NorwaySpruce', 'Sweetgum'):
        sp0 = 'unknown'
    new = None
    if sp0 in ('RedMaple', 'SugarMaple', 'PinOak', 'LondonPlane'):
        top_h = zmax * sz            # crown top above the trunk base (origin) = LiDAR-fit top
        r = h(name, 'az_sp')
        if r < 0.035 and top_h > 8.0: new = 'NorwaySpruce'
        elif 0.035 <= r < 0.07: new = 'Sweetgum'
        elif o.get('az_src_species'): new = 'Sweetgum'   # 2 north trees swapped by the 9:24 PM first pass (droop-inflated height) stay swapped
    if new:
        me = mesh['Tree_%s_LOD1' % new]; a, b = Z[me.name]
        s = top_h / max(b, 0.1)
        if new == 'NorwaySpruce':
            sx = sy = 0.88 + 0.20 * h(name, 'az_w'); lean = math.radians(1.0 * h(name, 'lean'))
        else:
            sx = 0.84 + 0.34 * h(name, 'az_sx'); sy = 0.84 + 0.34 * h(name, 'az_sy'); lean = math.radians(2.5 * h(name, 'lean'))
        la = 2 * math.pi * h(name, 'lea'); yaw = o.rotation_euler.z
        if not o.get('az_src_mesh'): o['az_src_mesh'] = mname
        o['az_src_species'] = sp0
        o.data = me; o.scale = (s * sx, s * sy, s); o.location.z = lz
        o.rotation_euler = Euler((lean * math.cos(la), lean * math.sin(la), yaw), 'XYZ')
        lo, hi = AUT[new]; o['autumn'] = lo + (hi - lo) * (h(name, 'az_aut') ** 0.85)
        o['ax_species'] = new; moved += 1
    elif o.get('ax_species') == 'WhitePine' and mname == 'Tree_WhitePine_LOD1':
        if zmin > 0.5:
            o.location.z = lz - zmin * sz; o['az_pine_gfix'] = round(zmin * sz, 2); pine += 1
        else:
            o.location.z = lz
    o['az_var'] = 1
    stats[o['ax_species']] = stats.get(o['ax_species'], 0) + 1
print('TREES', which, len(PRE), 'swapped', moved, 'pine_grounded', pine, stats)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath)

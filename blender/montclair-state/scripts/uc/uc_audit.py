"""Session uc: audit context wall-top vs roof gaps (Freeman-style).
For each '* walls' object that has a matching '* roof*' slab, compare wall top-z vs roof median z.
Flag gaps >= 0.5 m. Skip University Hall. Prefer day-9 vicinity for reporting.
Writes data/uc/wall_roof_gap_audit.json + .md
"""
import bpy, json, os, math
from collections import defaultdict

OUT_DIR = '/workspace/nj-scenes/montclair-state/data/uc'
os.makedirs(OUT_DIR, exist_ok=True)
GAP_THRESH = 0.5  # metres

# Day-9 / courtyard vicinity (approx) for priority ranking
DAY9_BOX = dict(xmin=-350, xmax=50, ymin=-50, ymax=250)  # Normal Ave / College Hall / Partridge / Freeman courtyard

def bbox(obj):
    xs, ys, zs = [], [], []
    mw = obj.matrix_world
    for v in obj.data.vertices:
        c = mw @ v.co
        xs.append(c.x); ys.append(c.y); zs.append(c.z)
    if not xs:
        return None
    return dict(xmin=min(xs), xmax=max(xs), ymin=min(ys), ymax=max(ys),
                zmin=min(zs), zmax=max(zs), nverts=len(xs))

def in_day9(bb):
    if not bb: return False
    # overlap test
    return not (bb['xmax'] < DAY9_BOX['xmin'] or bb['xmin'] > DAY9_BOX['xmax'] or
                bb['ymax'] < DAY9_BOX['ymin'] or bb['ymin'] > DAY9_BOX['ymax'])

def roof_median_z(obj):
    """Median z of up-facing / high verts (roof slab)."""
    mw = obj.matrix_world
    zs = [(mw @ v.co).z for v in obj.data.vertices]
    if not zs: return None
    zs = sorted(zs)
    return zs[len(zs)//2], zs[0], zs[-1], len(zs)

def wall_top_stats(obj, roof_z, band=8.0):
    """Stats on verts within `band` metres of roof_z (candidate tops) and overall top percentile."""
    mw = obj.matrix_world
    zs = sorted((mw @ v.co).z for v in obj.data.vertices)
    if not zs: return None
    zmax = zs[-1]
    # top 25% verts by z as "top band"
    n = max(1, len(zs)//4)
    top = zs[-n:]
    # verts that should meet roof: those in top band or within band of roof
    near_roof = [z for z in zs if z > roof_z - band]
    gap_max = roof_z - zmax  # positive => wall below roof
    # per-vert shortfalls among near-roof candidates that are still below roof-0.5
    shortfalls = [roof_z - z for z in near_roof if z < roof_z - 0.05]
    return dict(
        zmin=zs[0], zmax=zmax, nverts=len(zs),
        top25_min=top[0], top25_med=top[len(top)//2], top25_max=top[-1],
        near_roof_n=len(near_roof),
        shortfall_n=len(shortfalls),
        shortfall_max=max(shortfalls) if shortfalls else 0.0,
        shortfall_med=(sorted(shortfalls)[len(shortfalls)//2] if shortfalls else 0.0),
        gap_wall_max_to_roof=gap_max,
    )

# Index objects
walls = {}
roofs = {}
others = []
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    name = o.name
    low = name.lower()
    if 'university hall' in low:
        continue  # never touch
    if low.endswith(' walls') or ' walls' in low and 'wall' in low.split()[-1:]:
        walls[name] = o
    elif 'roof' in low:
        roofs[name] = o

# Also catch names like "Freeman Hall walls" / "X roof (LiDAR)"
# Build matching by shared building prefix
def prefix(n):
    # strip trailing walls / roof...
    for suf in (' walls', ' Walls', ' roof (LiDAR)', ' roof', ' Roof', ' roofs'):
        if n.endswith(suf):
            return n[:-len(suf)].strip()
    if ' roof' in n.lower():
        i = n.lower().index(' roof')
        return n[:i].strip()
    if ' walls' in n.lower():
        i = n.lower().index(' walls')
        return n[:i].strip()
    return n

wall_by_pref = defaultdict(list)
roof_by_pref = defaultdict(list)
for n, o in walls.items():
    wall_by_pref[prefix(n)].append((n, o))
for n, o in roofs.items():
    roof_by_pref[prefix(n)].append((n, o))

results = []
all_prefs = sorted(set(wall_by_pref) | set(roof_by_pref))
for pref in all_prefs:
    wlist = wall_by_pref.get(pref, [])
    rlist = roof_by_pref.get(pref, [])
    if not wlist or not rlist:
        results.append(dict(
            prefix=pref,
            walls=[n for n,_ in wlist],
            roofs=[n for n,_ in rlist],
            status='no_pair',
            day9=False,
        ))
        continue
    # use first/largest roof and first wall for primary compare; also check all combos
    for wn, wo in wlist:
        wbb = bbox(wo)
        best = None
        for rn, ro in rlist:
            rmed, rmin, rmax, rnverts = roof_median_z(ro)
            st = wall_top_stats(wo, rmed)
            gap = st['gap_wall_max_to_roof'] if st else None
            short_max = st['shortfall_max'] if st else None
            # significant open band: wall max clearly below roof, OR many top verts short
            sig_gap = (gap is not None and gap >= GAP_THRESH) or (short_max is not None and short_max >= GAP_THRESH and st['shortfall_n'] >= 4)
            entry = dict(
                wall=wn, roof=rn,
                roof_z_med=round(rmed, 3), roof_z_min=round(rmin,3), roof_z_max=round(rmax,3),
                roof_nverts=rnverts,
                wall_stats={k:(round(v,3) if isinstance(v,float) else v) for k,v in st.items()} if st else None,
                gap_m=round(gap,3) if gap is not None else None,
                shortfall_max_m=round(short_max,3) if short_max is not None else None,
                significant=bool(sig_gap),
                day9=in_day9(wbb),
                wall_bbox=({k:round(v,2) if isinstance(v,float) else v for k,v in wbb.items()} if wbb else None),
            )
            if best is None or (entry['gap_m'] or -999) > (best['gap_m'] or -999):
                best = entry
        results.append(dict(prefix=pref, **best, status='paired'))

# Sort: significant day9 first, then significant, then by gap
def sort_key(r):
    if r.get('status') != 'paired':
        return (2, 0, r.get('prefix',''))
    sig = 0 if r.get('significant') else 1
    d9 = 0 if r.get('day9') else 1
    gap = -(r.get('gap_m') or r.get('shortfall_max_m') or 0)
    return (sig, d9, gap, r.get('prefix',''))

results.sort(key=sort_key)

sig = [r for r in results if r.get('significant')]
sig_d9 = [r for r in sig if r.get('day9')]
paired = [r for r in results if r.get('status')=='paired']

report = dict(
    gap_thresh_m=GAP_THRESH,
    n_wall_objs=len(walls),
    n_roof_objs=len(roofs),
    n_paired=len(paired),
    n_significant=len(sig),
    n_significant_day9=len(sig_d9),
    freeman_note='Freeman already fixed by ub (tops at 147.05); expect gap~-0.05 or small',
    significant=sig,
    all_paired=paired,
    unpaired=[r for r in results if r.get('status')=='no_pair'],
)

with open(os.path.join(OUT_DIR, 'wall_roof_gap_audit.json'), 'w') as f:
    json.dump(report, f, indent=2)

# Markdown summary
lines = [
    '# Wall-top vs roof gap audit — session uc',
    '',
    f'Threshold: gaps ≥ {GAP_THRESH} m flagged.',
    f'Paired wall/roof buildings: {len(paired)}; significant gaps: {len(sig)} (day-9 vicinity: {len(sig_d9)}).',
    'University Hall skipped. Freeman Hall already fixed by ub.',
    '',
    '## Significant gaps (fix candidates)',
    '',
]
if not sig:
    lines.append('_None found._')
else:
    lines.append('| Building | Wall | Roof | Roof z med | Wall zmax | Gap m | Shortfall max | Day9 |')
    lines.append('|---|---|---|---:|---:|---:|---:|:---:|')
    for r in sig:
        ws = r.get('wall_stats') or {}
        lines.append('| {prefix} | {wall} | {roof} | {roof_z_med} | {wz} | {gap_m} | {sf} | {d9} |'.format(
            prefix=r.get('prefix',''), wall=r.get('wall',''), roof=r.get('roof',''),
            roof_z_med=r.get('roof_z_med'), wz=ws.get('zmax'), gap_m=r.get('gap_m'),
            sf=r.get('shortfall_max_m'), d9='Y' if r.get('day9') else ''))

lines += ['', '## All paired (sorted significant/day9 first)', '']
for r in paired:
    ws = r.get('wall_stats') or {}
    flag = ' **GAP**' if r.get('significant') else ''
    d9 = ' [day9]' if r.get('day9') else ''
    lines.append(f"- {r.get('prefix')}: wall zmax={ws.get('zmax')} roof_med={r.get('roof_z_med')} gap={r.get('gap_m')} shortfall_max={r.get('shortfall_max_m')}{flag}{d9}")

md = '\n'.join(lines) + '\n'
with open(os.path.join(OUT_DIR, 'wall_roof_gap_audit.md'), 'w') as f:
    f.write(md)

print('UC_AUDIT paired', len(paired), 'significant', len(sig), 'day9_sig', len(sig_d9))
for r in sig[:30]:
    ws = r.get('wall_stats') or {}
    print(f"  GAP {r.get('prefix')!r}: wall={r.get('wall')!r} roof_med={r.get('roof_z_med')} wall_zmax={ws.get('zmax')} gap={r.get('gap_m')} short_max={r.get('shortfall_max_m')} day9={r.get('day9')}")
print('UC_AUDIT wrote', OUT_DIR)

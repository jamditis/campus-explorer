"""Session ua survey: Normal Ave / south edge vs existing MAIN ground (read-only)."""
import bpy, json, math
from mathutils import Vector
from pathlib import Path
OUT = Path('/workspace/nj-scenes/montclair-state/data/ua/survey.md')
OUT.parent.mkdir(parents=True, exist_ok=True)
lines = []
def p(s=''):
    lines.append(s); print(s)

p('# Session ua survey — Normal Ave edge vs MAIN')
p()
p(f'Objects in blend: {len(bpy.data.objects)}')
p()

# Key ground/road objects
keys = ('Roads_OSM','Footpaths_OSM','Quad','Webster','Valley','Normal','Terrain','Context_skirt','Context_ground','Promenade','SB_','SG_','TY_','College','Cole','Partridge','Nursing')
interesting = []
for o in bpy.data.objects:
    n = o.name
    if any(k.lower() in n.lower() for k in keys) or o.get('ua_obj') or o.get('sg_obj') or o.get('ty_obj'):
        interesting.append(o)

def bbox_world(o):
    if o.type != 'MESH' or not o.bound_box:
        return None
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = (min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))
    hi = (max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb))
    return lo, hi

p('## Key objects (roads / terrain / walks / south campus)')
for o in sorted(interesting, key=lambda x: x.name):
    bb = bbox_world(o)
    cols = [c.name for c in o.users_collection]
    if bb:
        lo,hi = bb
        p(f'- `{o.name}` type={o.type} hide={o.hide_get()}/{o.hide_render} cols={cols[:3]} bbox=[{lo[0]:.1f},{lo[1]:.1f},{lo[2]:.1f}]→[{hi[0]:.1f},{hi[1]:.1f},{hi[2]:.1f}]')
    else:
        p(f'- `{o.name}` type={o.type} hide={o.hide_get()}/{o.hide_render} cols={cols[:3]} loc={tuple(round(x,2) for x in o.location)}')

# Terrain / skirt southern extent
p()
p('## Terrain / skirt extents')
for name in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','Context_ground_beyond_data','BD_farfield_3DEP_ortho','Roads_OSM','Footpaths_OSM'):
    o = bpy.data.objects.get(name)
    if not o:
        p(f'- MISSING `{name}`'); continue
    bb = bbox_world(o)
    if bb:
        lo,hi = bb
        p(f'- `{name}` verts={len(o.data.vertices) if o.type=="MESH" else "?"} xy=[{lo[0]:.1f}..{hi[0]:.1f}] × [{lo[1]:.1f}..{hi[1]:.1f}] z=[{lo[2]:.1f}..{hi[2]:.1f}]')

# Sample ground z along Normal Ave stations that are near half_m
bi = json.load(open('/workspace/nj-scenes/montclair-state/north/data/day_heroes/day9_normal_ave_edge_prep_20261016bi.json'))
dg = bpy.context.evaluated_depsgraph_get()
GN = ['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','QW_DTM_north_edge_ramp_UNVERIFIED','RZ2_SC_LiDAR_ground_patch','SA_ground_lower_patch_UNVERIFIED','QM_terrain_band_underlay_UNVERIFIED','QJ_NE_seam_fill_UNVERIFIED']
gnd = []
for n in GN:
    o = bpy.data.objects.get(n)
    if o: gnd.append((o.evaluated_get(dg), o.matrix_world, n))

def gz(x,y):
    best=None; hitn=None
    for e,mw,n in gnd:
        iw=mw.inverted()
        r=e.ray_cast(iw@Vector((x,y,400)), (iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best:
                best=z; hitn=n
    return best, hitn

p()
p('## Normal Ave stations near MAIN half_m=250 (sample every ~25 m where |x|<=280 or |y|<=280)')
HALF=250
near_count=0
for w in bi['ways']:
    st = w.get('stations_5m') or []
    near=[]
    for s in st:
        dist,x,y,z,src = s[0],s[1],s[2],s[3],s[4]
        if abs(x)<=280 or abs(y)<=280 or (abs(x)<=320 and abs(y)<=320):
            near.append(s)
    if not near:
        # also report closest station to origin / to (0,-250)
        best=min(st, key=lambda s: math.hypot(s[1], s[2]+250)) if st else None
        p(f"- way {w['id']} `{w.get('name')}` len={w.get('length_m')} — 0 stations near half; closest-to-S-edge={best}")
        continue
    p(f"- way {w['id']} `{w.get('name')}` hw={w.get('highway')} width={w.get('width_curb_m')} sidewalk={w.get('sidewalk_tag')} n_near={len(near)}")
    for s in near[::5]:
        dist,x,y,z,src=s[0],s[1],s[2],s[3],s[4]
        gz_,hn=gz(x,y)
        inside = abs(x)<=HALF and abs(y)<=HALF
        near_count += 1
        p(f"  sta {dist:.0f}m xy=({x:.1f},{y:.1f}) dem_z={z:.2f} ground={None if gz_ is None else round(gz_,2)} via={hn} inside_half={inside}")

p()
p(f'Near-station samples written: {near_count}')

# Roads_OSM face/vert sample in south half
roads=bpy.data.objects.get('Roads_OSM')
if roads:
    me=roads.data; mw=roads.matrix_world
    ys=[]; xs=[]; south=[]
    for v in me.vertices:
        pnt=mw@v.co
        xs.append(pnt.x); ys.append(pnt.y)
        if pnt.y < -100:
            south.append((pnt.x,pnt.y,pnt.z))
    p()
    p(f'## Roads_OSM extent xy=[{min(xs):.1f}..{max(xs):.1f}]×[{min(ys):.1f}..{max(ys):.1f}] nverts={len(me.vertices)} south(y<-100)={len(south)}')
    if south:
        south.sort(key=lambda t:t[1])
        p(f'  southernmost 8 verts: {[(round(a,1),round(b,1),round(c,2)) for a,b,c in south[:8]]}')
        p(f'  northernmost of south band: {[(round(a,1),round(b,1),round(c,2)) for a,b,c in south[-5:]]}')

fp=bpy.data.objects.get('Footpaths_OSM')
if fp:
    me=fp.data; mw=fp.matrix_world
    ys=[]; xs=[]; south=[]
    for v in me.vertices:
        pnt=mw@v.co
        xs.append(pnt.x); ys.append(pnt.y)
        if pnt.y < -50:
            south.append((pnt.x,pnt.y,pnt.z))
    p(f'## Footpaths_OSM extent xy=[{min(xs):.1f}..{max(xs):.1f}]×[{min(ys):.1f}..{max(ys):.1f}] nverts={len(me.vertices)} south(y<-50)={len(south)}')
    if south:
        south.sort(key=lambda t:t[1])
        p(f'  southernmost 8: {[(round(a,1),round(b,1),round(c,2)) for a,b,c in south[:8]]}')

# College / Cole / Partridge locations
p()
p('## South-campus buildings (College / Partridge / University Hall)')
for o in bpy.data.objects:
    nl=o.name.lower()
    if any(k in nl for k in ('cole','college','partridge','nursing','university hall','susan')) and o.type=='MESH':
        bb=bbox_world(o)
        if bb:
            lo,hi=bb
            if hi[1] < 200:  # roughly south half / mid
                p(f'- `{o.name}` xy=[{lo[0]:.1f}..{hi[0]:.1f}]×[{lo[1]:.1f}..{hi[1]:.1f}]')

# Existing SG/SF roads southern tip
p()
p('## Modelled road ribbons (SG/SF) tips')
for o in bpy.data.objects:
    if o.name.startswith(('SG_','SF_')) and ('Road' in o.name or 'road' in o.name or 'Walk' in o.name or 'walk' in o.name or 'foot' in o.name.lower()):
        bb=bbox_world(o)
        if bb:
            lo,hi=bb
            p(f'- `{o.name}` xy=[{lo[0]:.1f}..{hi[0]:.1f}]×[{lo[1]:.1f}..{hi[1]:.1f}]')

# Scene half from scene_data
sd=json.load(open('/workspace/nj-scenes/montclair-state/data/scene_data.json'))
p()
p(f"## scene_data half_m={sd['half_m']} (MAIN data square ≈ ±{sd['half_m']} m)")
p('Normal Ave OSM centreline is largely OUTSIDE this square (x mostly ≪ -500, y ~-270…-185).')
p()
p('## Candidate in-scene work')
p('1. Do NOT build the full 680 m CR 618 ribbon (x -1242…-575) — floats far off-campus.')
p('2. Check whether Context_skirt covers any Normal Ave stations near SW corner (x~-250,y~-270).')
p('3. Prefer campus-side walks already in scene_data south band that lack ribbons near College Hall / south promenade.')
p('4. Valley Road (OSM 312841179) is in scene_data as secondary CR 621 — check if Roads_OSM already covers it.')

OUT.write_text('\n'.join(lines)+'\n')
print('WROTE', OUT, 'lines', len(lines))

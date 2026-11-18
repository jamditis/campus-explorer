"""Ortho vs OSM Normal Ave curb/walk probe (no blend write).
Uses skirt NAIP/ortho (±2000 m) since Normal Ave is south of ortho2020 ±250 m.
Also samples MAIN ortho2020 for College Ave inside the half-extent.
"""
import json, math
from pathlib import Path
from PIL import Image
import numpy as np

OUT = Path('/workspace/nj-scenes/montclair-state/data/ua')
OUT.mkdir(exist_ok=True)
bi = json.load(open('/workspace/nj-scenes/montclair-state/north/data/day_heroes/day9_normal_ave_edge_prep_20261016bi.json'))
sd = json.load(open('/workspace/nj-scenes/montclair-state/data/scene_data.json'))
F = {str(f['id']): f for f in sd['features']}

# MAIN ortho ±250 m, 2048 px
o2020 = np.asarray(Image.open('/workspace/nj-scenes/montclair-state/data/ortho2020.png').convert('RGB'))
S2020 = 2048 / 500.0  # px per m
# Skirt ortho ±2000 m
sko = np.asarray(Image.open('/workspace/nj-scenes/montclair-state/data/skirt_ortho.jpg').convert('RGB'))
# Prefer NAIP 4k if present (same UV mapping)
naip_p = Path('/workspace/nj-scenes/montclair-state/data/ts/naip_skirt_4k.jpg')
if naip_p.exists():
    sko = np.asarray(Image.open(naip_p).convert('RGB'))
    print('Using NAIP skirt 4k', sko.shape)
else:
    print('Using skirt_ortho', sko.shape)
Hsk, Wsk = sko.shape[:2]
Ssk = Hsk / 4000.0  # px per m for ±2000

def sample_skirt(x, y):
    u = (x + 2000) / 4000; v = (y + 2000) / 4000
    if not (0 <= u < 1 and 0 <= v < 1):
        return None
    c = int(u * Wsk); r = int((1 - v) * Hsk)  # image row 0 = north? check UV: Blender UV v often bottom-up
    # In build_scene UV was (x+2000)/4000, (y+2000)/4000 with image typically v=0 at bottom
    # For numpy array row 0 = top of image. If Blender UV v maps bottom->top of image when Image Texture,
    # row = (1-v)*H. We'll try both and report luminance.
    r = max(0, min(Hsk-1, int((1-v)*Hsk))); c = max(0, min(Wsk-1, int(u*Wsk)))
    return sko[r, c].astype(float)

def sample_2020(x, y):
    if abs(x) > 250 or abs(y) > 250: return None
    u = (x + 250) / 500; v = (y + 250) / 500
    c = max(0, min(2047, int(u * 2048))); r = max(0, min(2047, int((1-v)*2048)))
    return o2020[r, c].astype(float)

def is_asphalt(rgb):
    if rgb is None: return None
    r,g,b = rgb
    lum = (r+g+b)/3
    # asphalt: low-mid grey, not green
    greenish = g > r + 15 and g > b + 10
    return (not greenish) and 40 < lum < 160, lum, greenish

lines = ['# ua ortho probe — Normal Ave edge', '']
# Probe Normal Ave ways near campus along centreline and ± half-width
report = []
for w in bi['ways']:
    wid = w['id']
    st = w.get('stations_5m') or []
    # keep stations with |x|<300 and y > -340 (near MAIN south)
    near = [s for s in st if abs(s[1]) < 320 and s[2] > -340]
    if not near: continue
    width = float(w.get('width_curb_m') or 7.3)
    asphalt_hits = 0; green_hits = 0; n = 0
    samples = []
    for s in near[::2]:
        dist,x,y = s[0],s[1],s[2]
        # estimate tangent from neighbours
        # offset left/right by width/2
        # find local tangent from stations list
        idx = st.index(s) if s in st else 0
        a = st[max(0, idx-1)]; b = st[min(len(st)-1, idx+1)]
        tx,ty = b[1]-a[1], b[2]-a[2]; L = math.hypot(tx,ty) or 1
        nx,ny = -ty/L, tx/L
        pts = [(x,y,'C'), (x+nx*width/2, y+ny*width/2, 'L'), (x-nx*width/2, y-ny*width/2, 'R'),
               (x+nx*(width/2+2.0), y+ny*(width/2+2.0), 'LN'), (x-nx*(width/2+2.0), y-ny*(width/2+2.0), 'RN')]
        row = {'sta': dist, 'xy': (round(x,1), round(y,1))}
        for px,py,lab in pts:
            rgb = sample_skirt(px, py)
            ok, lum, gr = is_asphalt(rgb) if rgb is not None else (None, None, None)
            row[lab] = None if lum is None else (round(lum,1), 'ASP' if ok else ('GRN' if gr else 'OTH'))
            if lab == 'C' and ok is not None:
                n += 1
                if ok: asphalt_hits += 1
                if gr: green_hits += 1
        samples.append(row)
    pct = 100*asphalt_hits/max(1,n)
    lines.append(f"## way {wid} `{w.get('name')}` hw={w.get('highway')} sidewalk={w.get('sidewalk_tag')} width={width} near_n={len(near)}")
    lines.append(f"centre asphalt-ish {asphalt_hits}/{n} ({pct:.0f}%), green {green_hits}/{n}")
    for row in samples[:12]:
        lines.append(f"  {row}")
    lines.append('')
    report.append({'id': wid, 'name': w.get('name'), 'pct_asphalt': pct, 'n': n, 'sidewalk': w.get('sidewalk_tag'), 'width': width})

# College Avenue approaches
for cid in ('232844571', '1557427669', '232846698', '312845863', '312845871', '312845873'):
    f = F.get(cid)
    if not f: 
        lines.append(f'## OSM {cid} NOT in scene_data'); continue
    pts = f['pts']; tags = f['tags']
    lines.append(f"## scene_data {cid} `{tags.get('name')}` hw={tags.get('highway')} npts={len(pts)}")
    asp=0; n=0
    for i, (x,y) in enumerate(pts):
        rgb = sample_skirt(x,y) if (abs(x)>250 or abs(y)>250) else sample_2020(x,y)
        # also try skirt always
        rgb2 = sample_skirt(x,y)
        ok,lum,gr = is_asphalt(rgb2)
        if ok is not None:
            n+=1
            if ok: asp+=1
        if i % max(1, len(pts)//8) == 0:
            lines.append(f"  pt{i} ({x:.1f},{y:.1f}) lum={None if lum is None else round(lum,1)} {'ASP' if ok else ('GRN' if gr else 'OTH')}")
    lines.append(f"  asphalt-ish {asp}/{n}")
    lines.append('')

# Save annotated crop of skirt around Normal Ave near campus
# Region x -280..-40, y -330..-240
x0,x1,y0,y1 = -280, -40, -330, -240
# Convert to pixel box
def xy_to_rc(x,y):
    u=(x+2000)/4000; v=(y+2000)/4000
    c=int(u*Wsk); r=int((1-v)*Hsk)
    return r,c
r0,c0 = xy_to_rc(x0,y1)  # NW
r1,c1 = xy_to_rc(x1,y0)  # SE
r0,r1 = sorted([max(0,r0), min(Hsk-1,r1)])
c0,c1 = sorted([max(0,c0), min(Wsk-1,c1)])
crop = sko[r0:r1+1, c0:c1+1].copy()
# draw centreline samples as red dots
from PIL import ImageDraw
im = Image.fromarray(crop)
dr = ImageDraw.Draw(im)
for w in bi['ways']:
    for s in (w.get('stations_5m') or [])[::2]:
        x,y=s[1],s[2]
        if not (x0<=x<=x1 and y0<=y<=y1): continue
        r,c = xy_to_rc(x,y)
        rr,cc = r-r0, c-c0
        if 0<=rr<im.size[1] and 0<=cc<im.size[0]:
            dr.ellipse([cc-2,rr-2,cc+2,rr+2], fill=(255,40,40))
im.save(OUT/'ortho_normal_ave_near_campus.jpg')
lines.append(f'Saved crop {im.size} -> ortho_normal_ave_near_campus.jpg (red=OSM centreline stations)')
lines.append('')
lines.append('## Recommendation')
for r in report:
    lines.append(f"- way {r['id']}: {r['pct_asphalt']:.0f}% asphalt centre samples, sidewalk={r['sidewalk']}, width={r['width']}")
lines.append('Build: Normal Ave ribbon for ways with high asphalt agreement near campus (x>-280), soft ends; optional N sidewalk where sidewalk=separate; College Ave spur 1557427669 if asphalt agrees; NO signals/furniture.')

(OUT/'ortho_probe.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[-40:]))
print('WROTE', OUT/'ortho_probe.md')

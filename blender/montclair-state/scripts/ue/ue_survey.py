"""Survey Cole/College Hall for session ue east-face pass."""
import bpy, json, os
from mathutils import Vector

OUT = '/workspace/nj-scenes/montclair-state/data/ue/survey.md'
lines = []
def p(s=''):
    lines.append(s); print(s)

p('# College Hall survey — session ue (2026-11-05)')
p(f'Objects total: {len(bpy.data.objects)}')
p('')

keys = ('cole', 'college', 'cupola', 'susan', 'tw_cole', 'tz_', 'bq', 'ue_')
p('## Cole-related objects')
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    n = o.name.lower()
    if not (any(k in n for k in keys) or o.get('tw_obj') or o.get('tz_obj') or o.get('ue_obj') or o.get('bq_obj')):
        continue
    cols = [c.name for c in o.users_collection]
    mats = [s.material.name if s.material else '' for s in o.material_slots][:6]
    if o.type == 'MESH' and o.data and len(o.data.vertices):
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
        xs=[v.x for v in ws]; ys=[v.y for v in ws]; zs=[v.z for v in ws]
        bbox = (round(min(xs),2), round(max(xs),2), round(min(ys),2), round(max(ys),2), round(min(zs),2), round(max(zs),2))
        nv, nf = len(o.data.vertices), len(o.data.polygons)
    else:
        bbox, nv, nf = None, 0, 0
    tags = {k: o.get(k) for k in ('tw_obj','tz_obj','ue_obj','bq_obj') if o.get(k)}
    p(f'- {o.name!r} type={o.type} hide={o.hide_get()}/{o.hide_render} v={nv} f={nf} cols={cols} mats={mats} bbox={bbox} tags={tags}')

w = bpy.data.objects.get('Susan A. Cole Hall walls')
p('')
p('## Susan A. Cole Hall walls')
if w:
    names = [m.name if m else '' for m in w.data.materials]
    p(f'mats={names}')
    buckets = {'S':0,'N':0,'E':0,'W':0,'up':0,'dn':0,'other':0}
    cream = {'S':0,'N':0,'E':0,'W':0}
    cream_si = None
    for i,n in enumerate(names):
        if n and 'cream' in n.lower():
            cream_si = i
    # tw/tz use flipped normal for face dir
    for poly in w.data.polygons:
        nw = -(w.matrix_world.to_3x3() @ poly.normal).normalized()
        if abs(nw.z) > 0.55:
            buckets['up' if nw.z > 0 else 'dn'] += 1
            continue
        face = None
        if nw.y < -0.55: face = 'S'
        elif nw.y > 0.55: face = 'N'
        elif nw.x > 0.55: face = 'E'
        elif nw.x < -0.55: face = 'W'
        else:
            buckets['other'] += 1
            continue
        buckets[face] += 1
        if cream_si is not None and poly.material_index == cream_si:
            cream[face] += 1
    p(f'face counts (tw-flip) {buckets}')
    p(f'cream faces by dir {cream} cream_si={cream_si}')

# East ring edges
p('')
p('## East ring edges (from levels_prep)')
ring = json.load(open('/workspace/nj-scenes/montclair-state/north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
P = [Vector((x,y)) for x,y in ring]
if P[0] == P[-1]:
    P = P[:-1]
area = sum(P[i].x*P[(i+1)%len(P)].y - P[(i+1)%len(P)].x*P[i].y for i in range(len(P)))/2
p(f'ring n={len(P)} area_sign={area:.1f}')
for i in range(len(P)):
    a,b = P[i], P[(i+1)%len(P)]
    d = b-a; L=d.length
    if L < 0.5: continue
    t = d/L
    n = Vector((t.y, -t.x)) if area > 0 else Vector((-t.y, t.x))
    face = 'E' if n.x>0.55 else ('W' if n.x<-0.55 else ('N' if n.y>0.55 else ('S' if n.y<-0.55 else '?')))
    if face == 'E' or L > 15:
        mid = (a+b)/2
        p(f'  edge {i}: L={L:.2f} face={face} n=({n.x:.2f},{n.y:.2f}) mid=({mid.x:.1f},{mid.y:.1f}) a=({a.x:.1f},{a.y:.1f}) b=({b.x:.1f},{b.y:.1f})')

# Existing TZ windows bbox / z histogram
p('')
p('## TZ EN windows sample')
wo = bpy.data.objects.get('TZ_Cole_windows_EN_UNVERIFIED')
if wo and wo.type=='MESH':
    # island-ish: sample face centers
    zs=[]; xs=[]; eastish=0
    for poly in wo.data.polygons:
        c = wo.matrix_world @ poly.center
        zs.append(c.z); xs.append(c.x)
        if c.x > -75:
            eastish += 1
    p(f'verts={len(wo.data.vertices)} faces={len(wo.data.polygons)} z[{min(zs):.2f},{max(zs):.2f}] x[{min(xs):.1f},{max(xs):.1f}] faces_x>-75={eastish}')

# Footways near east wall
p('')
p('## Footway / walk objects near Cole east (x>-80,y<-80)')
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    if o.type != 'MESH' or not o.data or not len(o.data.vertices):
        continue
    nl = o.name.lower()
    if not any(k in nl for k in ('foot','walk','path','sidewalk','apron','plaza','portico')):
        continue
    ws = [o.matrix_world @ v.co for v in o.data.vertices]
    xs=[v.x for v in ws]; ys=[v.y for v in ws]
    if max(xs) < -90 or min(xs) > -40: continue
    if max(ys) < -140 or min(ys) > -70: continue
    p(f'- {o.name!r} x[{min(xs):.0f},{max(xs):.0f}] y[{min(ys):.0f},{max(ys):.0f}]')

p('')
p('## Collections TW_/TZ_/UE_')
for cn in sorted(c.name for c in bpy.data.collections):
    if cn.startswith(('TW_','TZ_','UE_','COLE')):
        c = bpy.data.collections[cn]
        p(f'- {cn}: {len(c.objects)} objs')

p('')
p('## Cams TZ_/TW_/UE_')
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    if o.type=='CAMERA' and o.name.startswith(('TZ_','TW_','UE_','BQ_','BR_','BU_')):
        p(f'- {o.name} loc=({o.location.x:.1f},{o.location.y:.1f},{o.location.z:.1f})')

open(OUT,'w').write('\n'.join(lines)+'\n')
print('WROTE', OUT)

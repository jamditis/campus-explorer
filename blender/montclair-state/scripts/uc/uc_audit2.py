"""Refine gap audit: true gap = roof_med - wall_zmax; also list Buildings_context; locate College/Freeman/Partridge."""
import bpy, json, os
from mathutils import Vector

OUT='/workspace/nj-scenes/montclair-state/data/uc'

def world_bb(o):
    mw=o.matrix_world
    xs,ys,zs=[],[],[]
    for v in o.data.vertices:
        c=mw@v.co; xs.append(c.x); ys.append(c.y); zs.append(c.z)
    return (min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)) if xs else None

# Find key buildings + context collection
keys=['Freeman','Cole','College','Partridge','Nursing','Morehead','Schmitt','Communication','Kasser','Life','Dickson','Calcia','Finley','Sprague','University']
print('=== KEY OBJECTS ===')
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    if o.type!='MESH': continue
    if any(k.lower() in o.name.lower() for k in keys):
        bb=world_bb(o)
        if bb:
            print(f"  {o.name!r:70s} x[{bb[0]:.1f},{bb[1]:.1f}] y[{bb[2]:.1f},{bb[3]:.1f}] z[{bb[4]:.1f},{bb[5]:.1f}] n={len(o.data.vertices)}")

print('\n=== COLLECTIONS with Buildings / context ===')
for c in bpy.data.collections:
    if 'build' in c.name.lower() or 'context' in c.name.lower() or 'wall' in c.name.lower():
        print(f"  coll {c.name!r} objs={len(c.objects)}")

# Buildings_context contents
for cname in ['Buildings_context','Buildings','Context_buildings']:
    c=bpy.data.collections.get(cname)
    if not c: continue
    print(f'\n=== {cname} ===')
    for o in sorted(c.objects, key=lambda x:x.name):
        if o.type!='MESH': continue
        print(f"  {o.name}")

# Pair by prefix properly and compute TRUE gap only
def pref(n):
    low=n.lower()
    for suf in [' walls',' roof (lidar)',' roof',' roofs']:
        if low.endswith(suf):
            return n[:len(n)-len(suf)].strip()
    if ' walls' in low:
        return n[:low.index(' walls')].strip()
    if ' roof' in low:
        return n[:low.index(' roof')].strip()
    return None

walls={}; roofs={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'university hall' in o.name.lower(): continue
    p=pref(o.name)
    if p is None: continue
    low=o.name.lower()
    if low.rstrip().endswith('walls') or ' walls' in low:
        walls[p]=o
    elif 'roof' in low:
        roofs[p]=o

print('\n=== TRUE GAPS (roof_med - wall_zmax) sorted ===')
rows=[]
for p in sorted(set(walls)&set(roofs)):
    wo,ro=walls[p],roofs[p]
    wz=[(wo.matrix_world@v.co).z for v in wo.data.vertices]
    rz=sorted((ro.matrix_world@v.co).z for v in ro.data.vertices)
    rmed=rz[len(rz)//2]
    wzmax=max(wz)
    # Also: how many top-quartile wall verts are ≥0.5m below roof?
    wz_s=sorted(wz)
    top=wz_s[-(max(1,len(wz_s)//4)):]
    below=[rmed-z for z in top if z < rmed-0.5]
    gap=rmed-wzmax
    # "open band" style: fraction of top verts below roof-0.5, and max shortfall among them
    open_band = len(below) >= max(4, len(top)//5) and (max(below) if below else 0) >= 0.5
    bb=world_bb(wo)
    # day9: Normal Ave / College / Partridge / courtyard ~ x -320..80, y -80..220
    d9 = bb and not (bb[1]<-320 or bb[0]>80 or bb[3]<-80 or bb[2]>220)
    rows.append((gap, open_band, p, wo.name, ro.name, rmed, wzmax, len(below), max(below) if below else 0, d9, bb))

rows.sort(key=lambda r: (-(1 if r[1] or r[0]>=0.5 else 0), -(1 if r[9] else 0), -max(r[0], r[8])))
for gap,ob,p,wn,rn,rmed,wzmax,nb,mb,d9,bb in rows:
    flag=''
    if gap>=0.5: flag+=' WALL_BELOW'
    if ob: flag+=' OPEN_BAND'
    if d9: flag+=' DAY9'
    print(f"  gap={gap:+.3f} top_below={nb}/{max(1,len(walls[p].data.vertices)//4)} max_short={mb:.3f} {p!r}{flag}")
    if bb: print(f"       bb x[{bb[0]:.0f},{bb[1]:.0f}] y[{bb[2]:.0f},{bb[3]:.0f}]")

# Also check objects named like '*walls*' that might not pair, and roof-only context
print('\n=== WALL-LIKE without roof pair ===')
for p,o in sorted(walls.items()):
    if p not in roofs:
        bb=world_bb(o); print(f"  {o.name!r} bb={bb and (round(bb[0],1),round(bb[1],1),round(bb[2],1),round(bb[3],1))}")

print('\n=== Objects with Freeman / Russ / College in name ===')
for o in bpy.data.objects:
    if any(k in o.name for k in ('Freeman','Russ Hall','College Hall','Cole Hall','Partridge','Nursing')):
        print(f"  {o.name!r} type={o.type} hide={o.hide_get()}")

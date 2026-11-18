"""Re-audit wall tops vs roof EAVE (p10 / low perimeter), not median — pitched roofs otherwise false-positive."""
import bpy, json, os, math
from mathutils import Vector

OUT='/workspace/nj-scenes/montclair-state/data/uc'

def pref(n):
    low=n.lower()
    for suf in [' walls',' roof (lidar)',' roof',' roofs']:
        if low.endswith(suf):
            return n[:len(n)-len(suf)].strip()
    if ' walls' in low: return n[:low.index(' walls')].strip()
    if ' roof' in low: return n[:low.index(' roof')].strip()
    return None

walls={}; roofs={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'university hall' in o.name.lower(): continue
    p=pref(o.name)
    if p is None: continue
    low=o.name.lower()
    if low.rstrip().endswith('walls') or (' walls' in low and 'skirt' not in low and 'base' not in low and 'gapfill' not in low and 'OO_' not in o.name and 'OR_' not in o.name and 'OV_' not in o.name and 'OW_' not in o.name and 'CELS' not in o.name and 'QE_ref' not in o.name and 'MG ' not in o.name and 'MO ' not in o.name and 'CCOM' not in o.name and 'Feliciano east' not in o.name):
        if 'walls' in low.split()[-1] or low.endswith('walls'):
            walls[p]=o
    elif 'roof' in low and 'barrel' not in low and 'hip' not in low and 'eave' not in low and 'membrane' not in low:
        roofs[p]=o

# Fix wall detection - simpler
walls={}; roofs={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'university hall' in o.name.lower(): continue
    n=o.name
    # exact pattern "X walls" / "X roof (LiDAR)"
    if n.endswith(' walls') and not any(n.startswith(p) for p in ('OO_','OR_','OV_','OW_','CCOM','CELS','MG ','MO ','QE_','Feliciano east')):
        walls[n[:-6]]=o
    elif n.endswith(' roof (LiDAR)') or n.endswith(' roof'):
        key=n.replace(' roof (LiDAR)','').replace(' roof','')
        roofs[key]=o

rows=[]
for p in sorted(set(walls)&set(roofs)):
    wo,ro=walls[p],roofs[p]
    # roof eave ≈ low percentile of roof verts (flat roofs: eave≈med≈max)
    rz=sorted((ro.matrix_world@v.co).z for v in ro.data.vertices)
    rmin,rmax=rz[0],rz[-1]
    rmed=rz[len(rz)//2]
    rp10=rz[max(0,int(0.10*len(rz)))]
    rp20=rz[max(0,int(0.20*len(rz)))]
    # For LiDAR roof slabs, the bottom of the slab is often soffit; eave top ≈ p10-p20 of UP-facing or just use low edge of top surface
    # Better: use faces with normal.z > 0.7, take their z p10 as eave-ish for pitched, med for flat
    up_zs=[]
    me=ro.data; mw=ro.matrix_world
    
    for f in me.polygons:
        nrm=(mw.to_3x3()@f.normal).normalized()
        if nrm.z>0.5:
            # face centre z
            c=mw@f.center
            up_zs.append(c.z)
    if up_zs:
        up_zs=sorted(up_zs)
        up_min,up_max=up_zs[0],up_zs[-1]
        up_p10=up_zs[max(0,int(0.10*len(up_zs)))]
        up_med=up_zs[len(up_zs)//2]
        eave=up_p10  # pitched: lower up-faces = eaves; flat: all similar
    else:
        up_min=up_max=up_p10=up_med=None
        eave=rp10
    flat = (rmax-rmin) < 1.0 or (up_max is not None and (up_max-up_min)<1.0)
    target = up_med if flat else eave  # flat: meet slab; pitched: meet eave

    wz=[(wo.matrix_world@v.co).z for v in wo.data.vertices]
    wzmax=max(wz)
    zmid=(min(wz)+wzmax)/2
    upper=[z for z in wz if z>=zmid]
    # gap vs target
    gap = target - wzmax
    short=[target-z for z in upper if z < target-0.5]
    freeman_style = gap >= 0.5 and len(short) >= max(4, len(upper)//5)
    # also: even if max meets, if many upper verts short by ≥0.5 (partial band like Freeman S end)
    partial = (not freeman_style) and len(short) >= max(8, len(upper)//3) and (max(short) if short else 0) >= 1.0

    bb_xs=[(wo.matrix_world@v.co).x for v in wo.data.vertices]
    bb_ys=[(wo.matrix_world@v.co).y for v in wo.data.vertices]
    d9 = not (max(bb_xs)<-320 or min(bb_xs)>80 or max(bb_ys)<-80 or min(bb_ys)>220)

    rows.append(dict(
        pref=p, flat=flat, target=round(target,3), eave=round(eave,3) if eave else None,
        roof_med=round(rmed,3), roof_span=round(rmax-rmin,3),
        up_span=round(up_max-up_min,3) if up_max is not None else None,
        wall_zmax=round(wzmax,3), gap=round(gap,3),
        n_upper=len(upper), n_short=len(short),
        max_short=round(max(short),3) if short else 0,
        freeman_style=freeman_style, partial=partial, day9=d9,
        ub_fix=bool(wo.get('ub_fix')),
        hide=wo.hide_get(),
    ))

rows.sort(key=lambda r: (0 if r['freeman_style'] else 1, 0 if r['partial'] else 1, 0 if r['day9'] else 1, -(r['gap'] if r['gap']>0 else r['max_short'])))

print('pref | flat | target | wall_zmax | gap | short | freeman | partial | day9')
for r in rows:
    flags=''
    if r['freeman_style']: flags+=' FIX'
    if r['partial']: flags+=' PARTIAL'
    if r['day9']: flags+=' D9'
    if r['ub_fix']: flags+=' (ub_done)'
    print(f"{r['pref'][:42]:42s} flat={r['flat']!s:5s} tgt={r['target']:7.2f} wz={r['wall_zmax']:7.2f} gap={r['gap']:+6.2f} short={r['n_short']:4d}/{r['n_upper']:<4d} maxS={r['max_short']:5.2f}{flags}")

fix=[r for r in rows if r['freeman_style'] or r['partial']]
json.dump(dict(all=rows, fix_candidates=fix), open(f'{OUT}/eave_audit.json','w'), indent=2)
print(f'\nFix candidates: {len(fix)}')
for r in fix:
    print(' ', r['pref'], 'freeman' if r['freeman_style'] else 'partial', 'gap', r['gap'], 'maxS', r['max_short'])

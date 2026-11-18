"""For each paired walls+roof: find top-rim verts (highest z in local XY bins), compare to roof BVH z.
Freeman-style = rim significantly below flat roof over a contiguous stretch."""
import bpy, json, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT='/workspace/nj-scenes/montclair-state/data/uc'

walls={}; roofs={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'university hall' in o.name.lower(): continue
    n=o.name
    if n.endswith(' walls') and not any(n.startswith(p) for p in ('OO_','OR_','OV_','OW_','CCOM','CELS','MG ','MO ','QE_','Feliciano east')):
        walls[n[:-6]]=o
    elif n.endswith(' roof (LiDAR)'):
        roofs[n[:-13]]=o

def roof_bvh(ro):
    mw=ro.matrix_world
    verts=[mw@v.co for v in ro.data.vertices]
    polys=[p.vertices[:] for p in ro.data.polygons]
    return BVHTree.FromPolygons([v[:] for v in verts], polys)

rows=[]
for p in sorted(set(walls)&set(roofs)):
    wo,ro=walls[p],roofs[p]
    mw=wo.matrix_world
    # roof flatness via up-face z span
    up=[]
    rmw=ro.matrix_world
    for f in ro.data.polygons:
        n=(rmw.to_3x3()@f.normal).normalized()
        if n.z>0.7: up.append((rmw@f.center).z)
    if not up: continue
    up=sorted(up); flat=(up[-1]-up[0])<1.5
    r_target = up[len(up)//2]  # med of up faces
    r_low = up[max(0,int(0.05*len(up)))]

    # Bin wall verts in 1m XY cells; keep max z per cell as rim candidate; then keep cells whose max is in top 40% of cell-maxes overall
    cells={}
    for v in wo.data.vertices:
        c=mw@v.co
        key=(int(math.floor(c.x)), int(math.floor(c.y)))
        if key not in cells or c.z>cells[key][2]:
            cells[key]=(c.x,c.y,c.z,v.index)
    cell_zs=sorted(z for _,_,z,_ in cells.values())
    if not cell_zs: continue
    thr=cell_zs[int(0.60*len(cell_zs))]  # upper 40% of cell maxes = rim-ish
    rim=[(x,y,z,i) for (x,y,z,i) in cells.values() if z>=thr]

    bvh=roof_bvh(ro)
    gaps=[]
    for x,y,z,i in rim:
        # ray up then down from above
        hit=bvh.ray_cast(Vector((x,y,z+30)), Vector((0,0,-1)))
        if hit[0] is None:
            hit=bvh.ray_cast(Vector((x,y,r_target+5)), Vector((0,0,-1)))
        if hit[0] is None:
            roof_z=r_target; hit_ok=False
        else:
            roof_z=hit[0].z; hit_ok=True
        gaps.append(dict(x=x,y=y,wall_z=z,roof_z=roof_z,gap=roof_z-z,idx=i,hit=hit_ok))

    gap_vals=[g['gap'] for g in gaps]
    bad=[g for g in gaps if g['gap']>=0.5]
    # contiguous-ish: count bad
    max_gap=max(gap_vals) if gap_vals else 0
    med_gap=sorted(gap_vals)[len(gap_vals)//2] if gap_vals else 0
    mean_bad=sum(g['gap'] for g in bad)/len(bad) if bad else 0

    bb_xs=[g['x'] for g in gaps]; bb_ys=[g['y'] for g in gaps]
    d9 = not (max(bb_xs)<-320 or min(bb_xs)>80 or max(bb_ys)<-80 or min(bb_ys)>220)

    # freeman-style on FLAT roofs: many rim cells gap>=0.5
    freeman = flat and len(bad)>=max(3, len(rim)//5) and max_gap>=0.5
    # also report near-flat with clear rim gaps
    notable = (len(bad)>=max(5,len(rim)//4) and max_gap>=0.8)

    rows.append(dict(
        pref=p, flat=flat, r_target=round(r_target,3), r_span=round(up[-1]-up[0],3),
        n_rim=len(rim), n_bad=len(bad), max_gap=round(max_gap,3), med_gap=round(med_gap,3),
        mean_bad=round(mean_bad,3), freeman=freeman, notable=notable, day9=d9,
        ub=bool(wo.get('ub_fix')),
        bad_sample=[{k:round(v,2) if isinstance(v,float) else v for k,v in g.items() if k!='idx'} for g in sorted(bad,key=lambda g:-g['gap'])[:5]],
    ))

rows.sort(key=lambda r:(0 if r['freeman'] else 1, 0 if r['notable'] else 1, 0 if r['day9'] else 1, -r['max_gap']))
print(f"{'pref':42s} flat rim bad maxG medG freeman notable d9')")
for r in rows:
    fl=''
    if r['freeman']: fl+=' FREEMAN'
    if r['notable']: fl+=' NOTABLE'
    if r['day9']: fl+=' D9'
    if r['ub']: fl+=' ub'
    print(f"{r['pref'][:42]:42s} F={r['flat']!s:5s} rim={r['n_rim']:3d} bad={r['n_bad']:3d} maxG={r['max_gap']:5.2f} medG={r['med_gap']:5.2f}{fl}")
    if r['freeman'] or r['notable'] or r['max_gap']>=0.5:
        for s in r['bad_sample'][:3]:
            print(f"    bad {s}")

json.dump(rows, open(f'{OUT}/perimeter_audit.json','w'), indent=2)
fix=[r for r in rows if r['freeman'] or (r['notable'] and r['flat'])]
print('\nFIX LIST:', [r['pref'] for r in fix])

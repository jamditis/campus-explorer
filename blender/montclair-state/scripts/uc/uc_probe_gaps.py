"""Per-building wall-top distribution vs roof for WALL_BELOW candidates; check visibility/hero overlays."""
import bpy, json, os
from collections import Counter

CANDS = [
    'Susan A. Cole Hall',
    'Morehead Hall',
    'Schmitt Hall',
    'School of Communication and Media',
    'Memorial Auditorium',
    'Calcia Hall',
    'Life Hall',
    'Feliciano School of Business',
    'Freeman Hall',  # already fixed baseline
]

def get(name):
    return bpy.data.objects.get(name)

out=[]
for pref in CANDS:
    wo=get(f'{pref} walls')
    # roof name variants
    ro=get(f'{pref} roof (LiDAR)') or get(f'{pref} roof')
    if not wo or not ro:
        print('MISSING', pref, wo, ro); continue
    wz=[(wo.matrix_world@v.co).z for v in wo.data.vertices]
    rz=sorted((ro.matrix_world@v.co).z for v in ro.data.vertices)
    rmed=rz[len(rz)//2]; rmin=rz[0]; rmax=rz[-1]
    # roof flatness
    rspan=rmax-rmin
    # wall top histogram in 0.5m bins relative to roof
    deltas=[rmed-z for z in wz]
    # only consider verts in upper half of wall height
    zmid=(min(wz)+max(wz))/2
    upper=[(i,z) for i,z in enumerate(wz) if z>=zmid]
    upper_short=[rmed-z for _,z in upper if z < rmed-0.25]
    # How many wall verts within 0.15 of roof (meeting)?
    meeting=sum(1 for z in wz if abs(z-rmed)<0.15 or z>=rmed-0.05)
    # Max continuous shortfall among upper verts
    max_short=max((rmed-z for _,z in upper), default=0)
    # Visibility
    hide=wo.hide_get(); hide_v=wo.hide_viewport; hide_r=wo.hide_render
    # Collections
    colls=[c.name for c in bpy.data.collections if wo.name in c.objects]
    # Any hero objects that might cover? sample objects with pref in name that aren't walls/roof
    heroes=[o.name for o in bpy.data.objects if pref.split()[0] in o.name and o.type=='MESH' and o!=wo and o!=ro and not o.hide_get()]
    # For Cole also check Cole Hall*
    if 'Cole' in pref:
        heroes += [o.name for o in bpy.data.objects if o.name.startswith('Cole Hall') and o.type=='MESH' and not o.hide_get()]
    # Material slots hint
    mats=[s.material.name if s.material else None for s in wo.material_slots][:3]
    # Top verts xy extent of those ≥0.5 below roof
    short_verts=[(wo.matrix_world@wo.data.vertices[i].co) for i,z in enumerate(wz) if z>=zmid and z<rmed-0.5]
    if short_verts:
        xs=[v.x for v in short_verts]; ys=[v.y for v in short_verts]
        short_bb=(min(xs),max(xs),min(ys),max(ys), min(v.z for v in short_verts), max(v.z for v in short_verts))
    else:
        short_bb=None
    row=dict(
        pref=pref, wall=wo.name, roof=ro.name,
        roof_med=round(rmed,3), roof_span=round(rspan,3),
        wall_zmin=round(min(wz),3), wall_zmax=round(max(wz),3),
        gap_max=round(rmed-max(wz),3),
        nverts=len(wz), n_upper=len(upper), n_upper_short025=len(upper_short),
        max_upper_short=round(max_short,3),
        n_meeting=meeting,
        hide=hide, hide_viewport=hide_v, hide_render=hide_r,
        colls=colls, mats=mats,
        n_heroes_visible=len(heroes), heroes_sample=heroes[:8],
        short_bb=([round(x,2) for x in short_bb] if short_bb else None),
        ub_fix=bool(wo.get('ub_fix')),
    )
    out.append(row)
    print(f"\n== {pref} ==")
    print(f"  roof_med={rmed:.3f} span={rspan:.3f} wall_z=[{min(wz):.3f},{max(wz):.3f}] gap_max={rmed-max(wz):+.3f}")
    print(f"  upper={len(upper)} upper_short>0.25={len(upper_short)} max_upper_short={max_short:.3f} meeting≈{meeting}")
    print(f"  hide={hide}/{hide_v}/{hide_r} colls={colls} ub_fix={wo.get('ub_fix')}")
    print(f"  short_bb={short_bb}")
    print(f"  heroes({len(heroes)}): {heroes[:6]}")

# Also: are Cole Hall walls the ones still rendering, or TW cream covers?
# Check if TW/TZ objects replaced wall faces or sit outside
print('\n=== Cole/TW related ===')
for o in bpy.data.objects:
    if 'Cole' in o.name or o.name.startswith('TW_') or o.name.startswith('TZ_'):
        if o.type=='MESH':
            print(f"  {o.name[:70]!r} hide={o.hide_get()} verts={len(o.data.vertices)}")

json.dump(out, open(f'{OUT}/probe_candidates.json','w'), indent=2)
print('\nWrote probe_candidates.json')

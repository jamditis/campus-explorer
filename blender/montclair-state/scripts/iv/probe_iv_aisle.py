# read-only: where do non-flat, non-vertical faces sit (crease candidates) relative to the aisle material?
import bpy, numpy as np
o=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=o.data
mats=[m.name for m in me.materials]; ai=mats.index('io_amphi_aisle_stone'); si=mats.index('hn_amphi_seat_stone_blocks'); ri=mats.index('hn_amphi_riser_coursed_stone')
aisle_v=set()
for p in me.polygons:
    if p.material_index==ai: aisle_v.update(p.vertices)
cnt={'near_aisle':0,'elsewhere':0}; areas={'near_aisle':0,'elsewhere':0}; xs=[]
for p in me.polygons:
    if p.material_index not in (si,ri): continue
    t=np.degrees(np.arccos(min(1,max(-1,p.normal.z))))
    if 8<t<55:
        k='near_aisle' if any(v in aisle_v for v in p.vertices) else 'elsewhere'
        cnt[k]+=1; areas[k]+=p.area
        if k=='near_aisle': xs.append(tuple(p.center))
print('IVA crease faces',cnt,{k:round(v,2) for k,v in areas.items()})
if xs:
    a=np.array(xs); print('IVA near-aisle bbox',a.min(0).round(1),a.max(0).round(1))

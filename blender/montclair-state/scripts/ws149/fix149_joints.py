# ws149: walk-end joint unification (WS147 square end slab, UNIFY #51 residual "no joints on the new walk end").
# Design: the slab must read as the same walk it ends; give it the joint material the adjoining walk faces use
# (majority material of Footpaths_OSM faces on the same walk x -69.4..-66.8, y -175..-160), else WS3 sawcut grid
# (world 1.8 m grid, the same grid as the WS143 forecourt/band it butts, so joints line up across the seam).
import bpy
from collections import Counter
fp=bpy.data.objects['Footpaths_OSM']; mw=fp.matrix_world; me=fp.data
cnt=Counter()
for p in me.polygons:
    c=mw@p.center
    if -69.4<c.x<-66.8 and -175.0<c.y<-160.0: cnt[p.material_index]+=1
slots=[s.material.name if s.material else None for s in fp.material_slots]
print("FIX149J_FP_MATS",{slots[k]:v for k,v in cnt.items()})
sl=[o for o in bpy.data.objects if o.name.startswith('WS147_walk_E_of_forecourt_square_end')]
want=slots[cnt.most_common(1)[0][0]] if cnt else 'WS3_Concrete_panels_sawcut'
if want=='WS4_Concrete_walk_broom_nogrid' and not cnt.get(1): pass
for o in sl:
    old=o.data.materials[0].name if o.data.materials else None
    m=bpy.data.materials.get('WS3_Concrete_panels_sawcut')
    o.data.materials[0]=m
    print("FIX149J_SLAB",o.name,old,"->",m.name,"(adjoining walk majority:",want,")")

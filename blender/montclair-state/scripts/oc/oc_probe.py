import bpy, mathutils
from collections import Counter
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
cnt=Counter(); rows=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>2 and lo[0]<13 and hi[1]>0 and lo[1]<16 and lo[2]<139.5 and hi[2]>137.3 and (hi[0]-lo[0])<20:
        rows.append((o.name,[round(x,2) for x in lo],[round(x,2) for x in hi],[s.material.name if s.material else None for s in o.material_slots][:2]))
for r in sorted(rows): print('P|',r)
for c in bpy.data.objects:
    if c.type=='CAMERA' and ('cafe' in c.name or 'east' in c.name.lower()) and c.name[:2] in ('NY','NX','NT','NQ'): print('CAM|',c.name,tuple(round(x,2) for x in c.location))

import bpy, bmesh
from mathutils import Vector
for o in bpy.data.objects:
  n=o.name
  if any(k in n for k in ('sign','Sign','WS4','WS3','WS5','lamp','Lamp')) and ('Cole' in n or 'WS' in n[:3]):
    print('OBJ',n,o.type,[round(v,2) for v in o.matrix_world.translation],[round(v,1) for v in o.dimensions], [m.name for m in getattr(o.data,'materials',[])][:4])
w=bpy.data.objects['WS3_Cole_plaza_paving_20261109']; mw=w.matrix_world
bm=bmesh.new(); bm.from_mesh(w.data)
import collections
cnt=collections.Counter()
for f in bm.faces:
  c=mw@f.calc_center_median(); cnt[(f.material_index, int(c.x//5)*5, int(c.y//5)*5)]+=1
for k,v in sorted(cnt.items()): print('CELL',k,v)
print('NV',len(bm.verts),'NF',len(bm.faces))

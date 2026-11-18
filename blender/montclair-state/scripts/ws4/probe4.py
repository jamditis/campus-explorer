import bpy
from mathutils import Vector
C=Vector((-140,-40))
for o in bpy.data.objects:
  if o.type not in ('MESH','EMPTY','CURVE'): continue
  n=o.name.lower()
  if not any(k in n for k in ('lamp','light','pole','arm','mast','lum','post','cobra','street')): continue
  cs=[o.matrix_world@Vector(c) for c in o.bound_box]
  lo=[min(c[i] for c in cs) for i in range(3)]; hi=[max(c[i] for c in cs) for i in range(3)]
  if lo[0]<-100 and hi[0]>-160 and lo[1]<-20 and hi[1]>-70 and (hi[0]-lo[0])<40:
    print('L',o.name,[round(x,1) for x in lo],[round(x,1) for x in hi],o.parent.name if o.parent else None,[c.name for c in o.users_collection][:1])

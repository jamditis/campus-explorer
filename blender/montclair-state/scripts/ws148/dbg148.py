import bpy, bmesh, numpy as np
from mathutils import Vector
a=[o for o in bpy.data.objects if o.name.startswith('WS142_Lot9_asphalt')][0]
print("DBG mw",[round(x,2) for x in a.matrix_world.translation],"nv",len(a.data.vertices),"nf",len(a.data.polygons))
vs=np.array([tuple(a.matrix_world@v.co) for v in a.data.vertices]); print("DBG vrange",vs.min(0).round(2),vs.max(0).round(2))
rows={}
for x,y in cells: rows.setdefault(round(y),[]).append(x)
for y in sorted(rows): print("DBG row",y,min(rows[y]),max(rows[y]),len(rows[y]))

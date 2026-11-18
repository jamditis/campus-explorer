import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if not n.startswith('T_') and not any(k in n.lower() for k in ('grass','tuft','clover','leaf','scatter','shrub','flower','annual'))]
for box,tag in (((5,22,-50,-34),'A'),((-28,-15,-18,-2),'D')):
    for o in to.objects:
        if not o or o.type not in ('MESH','CURVE'): continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        x0,x1=min(p.x for p in bb),max(p.x for p in bb); y0,y1=min(p.y for p in bb),max(p.y for p in bb)
        if x1<box[0] or x0>box[1] or y1<box[2] or y0>box[3]: continue
        if (x1-x0)>150 or (y1-y0)>150: continue
        print('NR',tag,o.name[:70],round(x0),round(x1),round(y0),round(y1),round(min(p.z for p in bb),1),round(max(p.z for p in bb),1))

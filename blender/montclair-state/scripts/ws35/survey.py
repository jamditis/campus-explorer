import bpy
from mathutils import Vector
out=[]
for o in bpy.data.objects:
    if o.type in ('CAMERA','LIGHT'): continue
    try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<-260 or min(xs)>-110 or max(ys)<-150 or min(ys)>40: continue
    if (max(xs)-min(xs))>400: continue
    nm=o.name
    out.append(f"{nm}|{o.type}|{min(xs):.1f},{max(xs):.1f}|{min(ys):.1f},{max(ys):.1f}|{min(zs):.2f},{max(zs):.2f}|{[c.name for c in o.users_collection][:1]}|hide={o.hide_render}")
open('/workspace/nj-scenes/montclair-state/scripts/ws35/survey.txt','w').write('\n'.join(sorted(out)))
print('N',len(out))

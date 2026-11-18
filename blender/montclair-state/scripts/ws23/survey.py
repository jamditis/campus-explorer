import bpy, json, sys
from mathutils import Vector
BX=(-430,-170,-290,70)
out=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','EMPTY','CAMERA','FONT'): continue
    try:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<BX[0] or min(xs)>BX[1] or max(ys)<BX[2] or min(ys)>BX[3]: continue
    span=(max(xs)-min(xs))*(max(ys)-min(ys))
    if span>2e5 and 'hawk' not in o.name.lower(): continue  # skip terrain-wide objects
    out.append(dict(n=o.name,t=o.type,bb=[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)),round(min(zs),1),round(max(zs),1)],
        f=len(o.data.polygons) if o.type=='MESH' else 0, hide=o.hide_render, coll=[c.name for c in o.users_collection][:1]))
hits=[o.name for o in bpy.data.objects if any(k in o.name.lower() for k in ('hawk','college_av','collegeav','normal','rhc','country'))]
tag=sys.argv[-1]
json.dump(dict(inbox=out,named=hits),open(f'data/ws23/survey_{tag}.json','w'),indent=0)
print('INBOX',len(out),'NAMED',len(hits))
for o in sorted(out,key=lambda d:-d['f'])[:60]: print(o)
print('NAMED',hits[:80])

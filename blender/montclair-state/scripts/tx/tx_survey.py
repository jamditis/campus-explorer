import bpy, mathutils
out=[]
keys=('nursing','313026395','partridge','grad')
cx,cy=-83.474,256.964
for o in sorted(bpy.data.objects, key=lambda x:x.name):
    n=o.name.lower()
    near=False
    if o.type=='MESH':
        bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        lo=(min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb)); hi=(max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb))
        near = lo[0]<cx+30 and hi[0]>cx-30 and lo[1]<cy+30 and hi[1]>cy-30 and (hi[0]-lo[0])<400
    else: lo=hi=None
    if any(k in n for k in keys) or near:
        cols=[c.name for c in o.users_collection]
        mats=[s.material.name if s.material else '' for s in o.material_slots]
        nv=len(o.data.vertices) if o.type=='MESH' else 0
        out.append(f"OBJ {o.name!r} hide={o.hide_get()}/{o.hide_render} v={nv} cols={cols[:2]} mats={mats[:4]} bbox={tuple(round(x,1) for x in lo) if lo else None}->{tuple(round(x,1) for x in hi) if hi else None}")
for o in bpy.data.objects:
    if o.type=='CAMERA' and any(k in o.name.lower() for k in keys): out.append(f"CAM {o.name} {tuple(round(x,1) for x in o.matrix_world.translation)}")
print('NOBJ',len(bpy.data.objects))
open('/workspace/nj-scenes/montclair-state/data/tx/survey.txt','w').write('\n'.join(out)+'\n')

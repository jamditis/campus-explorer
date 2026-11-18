import bpy, bmesh, json
from mathutils import Vector
out={}
curbs=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS27') and 'curb' in o.name.lower()]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith('WS72b'): continue
    me=o.data; bm=bmesh.new(); bm.from_mesh(me)
    bnd=[o.matrix_world@v.co for v in bm.verts if v.is_boundary]
    out[o.name]={'n':len(me.vertices),'bnd':[[round(c,3) for c in p] for p in bnd]}
    bm.free()
for c in curbs:
    vs=[c.matrix_world@v.co for v in c.data.vertices]
    out[c.name]={'n':len(vs),'sample':[[round(x,3) for x in p] for p in vs[::max(1,len(vs)//400)]]}
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws92/probe92a.json','w'))
print('P92 done',list(out.keys()))

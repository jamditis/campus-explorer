import bpy, bmesh
from mathutils import Vector
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; me=o.data
print('MW',[list(r) for r in o.matrix_world])
slots=[s.material.name for s in o.material_slots]; print('SLOTS',list(enumerate(slots)))
bm=bmesh.new(); bm.from_mesh(me)
import collections
# big vertical faces by normal direction
for f in bm.faces:
    if abs(f.normal.z)<0.1 and f.calc_area()>1.0:
        c=f.calc_center_median(); zs=[v.co.z for v in f.verts]
        print('F',f.index,'n',tuple(round(x,2) for x in f.normal),'c',tuple(round(x,2) for x in c),'A',round(f.calc_area(),2),'z',round(min(zs),2),round(max(zs),2),'m',f.material_index)
xs=[v.co.x for v in bm.verts]; ys=[v.co.y for v in bm.verts]; zs=[v.co.z for v in bm.verts]
print('BB',min(xs),max(xs),min(ys),max(ys),min(zs),max(zs))
cnt=collections.Counter(f.material_index for f in bm.faces); print('MATCOUNT',cnt)
for n in bpy.data.objects:
    if n.name.startswith(('WS16_Cole','WS15_Cole','TZ_Cole')): print('OBJ',n.name,n.type,[round(v,2) for v in n.location])

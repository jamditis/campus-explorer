# ws254 read-only: does the Sprague L0 east-strip mesh actually cover the Cafe Diem footprint (x -60..-43, y 35..71)?
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
L0=next(o for o in bpy.data.objects if o.name.startswith('Sprague Library L0 (LiDAR 141.8'))
bl=BVHTree.FromObject(L0,dg)
cafe=[o for o in bpy.data.objects if o.type=='MESH' and ('Diem' in o.name or 'cafe' in o.name.lower() or 'Cafe' in o.name) and not o.hide_render]
print('M4P cafe objs',len(cafe),[o.name[:50] for o in cafe][:15],flush=True)
bc=[BVHTree.FromObject(o,dg) for o in cafe]
grid=[]
for y in np.arange(35.5,71,2.0):
    row=''
    for x in np.arange(-59.5,-43,1.5):
        h=bl.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        c=[b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)[0] for b in bc]; cz=max([q.z for q in c if q] or [None]) if any(c) else None
        row+=('L' if h[0] and (cz is None or h[0].z>cz+0.05) else ('c' if cz else '.'))
    print('M4P y %5.1f '%y+row,flush=True)
os._exit(0)

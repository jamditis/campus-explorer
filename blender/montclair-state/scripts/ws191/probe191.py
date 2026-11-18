# ws191 probe (modifiers OFF, never saves): what lies at the #91 sliver candidates, raw skirt vs patch tops per object
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BOXES={'A':(-349.2,-346.8,-262.4,-235.8),'B':(-306.0,-299.8,-251.0,-248.0),'C':(-354.0,-347.6,-236.4,-233.2),'D':(-305.6,-297.8,-237.6,-233.4)}
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
cache={}
for k,(X0,X1,Y0,Y1) in BOXES.items():
    objs=[]
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
        if max(v.z for v in bb)-min(v.z for v in bb)>40 and not o.name.startswith('Context_skirt'): continue
        hid=o.hide_render or any(c.hide_render for c in o.users_collection)
        objs.append((o.name,hid,[m.name for m in o.modifiers]))
        if o.name not in cache: cache[o.name]=bvh(o)
    print('OBJS191',k,flush=True)
    for n,h,m in objs: print('  O',n,'HIDDEN' if h else '', m[:6])
    import numpy as np
    for x in np.arange(X0,X1+1e-6,0.4):
        for y in np.arange(Y0,Y1+1e-6,1.2 if k=='A' else 0.4):
            row=[]
            for n,h,m in objs:
                hit=cache[n].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
                if hit: row.append('%s%s=%.2f'%(n[:28],'(h)' if h else '',hit.z))
            print('  P %.1f %.1f'%(x,y),' | '.join(row))

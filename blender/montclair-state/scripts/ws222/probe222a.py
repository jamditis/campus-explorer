import bpy
from mathutils import Vector
# objects with verts in the W41b region (x -253..-251.0, y -55.6..-53.8)
X0,X1,Y0,Y1=-253.2,-251.0,-55.6,-53.6
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.vertices: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)>X1 or max(v.x for v in bb)<X0 or min(v.y for v in bb)>Y1 or max(v.y for v in bb)<Y0: continue
    if len(o.data.vertices)>400000: print('P222 BIG',o.name,len(o.data.vertices)); continue
    M=o.matrix_world; vs=[(i,M@v.co) for i,v in enumerate(o.data.vertices)]
    vs=[(i,w) for i,w in vs if X0<=w.x<=X1 and Y0<=w.y<=Y1]
    if not vs: continue
    # boundary edges
    from collections import Counter
    c=Counter()
    for p in o.data.polygons:
        for k in p.edge_keys: c[k]+=1
    bset=set(); [bset.update(k) for k,n in c.items() if n==1]
    bv=[(i,w) for i,w in vs if i in bset]
    print('P222 OBJ %s nv_in %d bnd_in %d mods %s mat %s'%(o.name,len(vs),len(bv),[m.type for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots][:3]))
    for i,w in sorted(bv,key=lambda t:t[1].x)[:40]:
        print('P222   b v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))

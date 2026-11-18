import bpy, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-236,-222,-234,-218
dg=bpy.context.evaluated_depsgraph_get()
trees=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('WS125_bed','WS126_bed','ShrubLeaf')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    vs=[mw@v.co for v in me.vertices]; ps=[tuple(p.vertices) for p in me.polygons]
    mats=[(me.materials[p.material_index].name if me.materials and p.material_index<len(me.materials) and me.materials[p.material_index] else '') for p in me.polygons]
    if ps: trees.append((o.name,BVHTree.FromPolygons(vs,ps),mats))
    oe.to_mesh_clear()
print('TREES',[t[0] for t in trees])
cnt=collections.Counter(); ex={}
x=X0
while x<=X1:
    y=Y0
    while y<=Y1:
        best=None
        for n,t,mats in trees:
            r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if r[0] is not None and (best is None or r[0].z>best[1]): best=(n,r[0].z,mats[r[2]])
        if best:
            k=best[0]+'|'+best[2]; cnt[k]+=1; ex.setdefault(k,[]).append((round(x,1),round(y,1),round(best[1],2)))
        y+=0.25
    x+=0.25
for n,c in cnt.most_common(): print('HIT',n,c,ex[n][:3])

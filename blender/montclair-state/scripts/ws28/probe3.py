import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
road=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']
# grid along road: sample road z and all hits above it
import math
out=[]
for y in range(-150,-100,2):
  for x in [i*0.5 for i in range(-440,-396)]:
    h=sc.ray_cast(dg,Vector((x,y,175)),Vector((0,0,-1)))
    # walk down through hits
    o=Vector((x,y,175)); hits=[]
    for k in range(8):
        h=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h[0]: break
        hits.append((h[4].name,round(h[1].z,2))); o=h[1]-Vector((0,0,0.002))
        if h[4]==road: break
    if any(n==road.name for n,_ in hits):
        rz=[z for n,z in hits if n==road.name][0]
        above=[(n,round(z-rz,2)) for n,z in hits if n!=road.name and not n.startswith('T_') and z>rz+0.01]
        if above: out.append((x,y,above[:3]))
from collections import Counter
c=Counter(a[0] for _,_,ab in out for a in ab)
print(c.most_common(20))
for r in out[:40]: print(r)
# grass-like objects
for o in sc.objects:
    if any(k in o.name.lower() for k in('grass','lawn','tuft','scatter')) and not o.hide_render:
        bb=[o.matrix_world@Vector(cc) for cc in o.bound_box]
        if min(b.x for b in bb)<-200 and max(b.x for b in bb)>-230 and min(b.y for b in bb)<-110 and max(b.y for b in bb)>-150: print('G',o.name,o.type,[m.type for m in o.modifiers])

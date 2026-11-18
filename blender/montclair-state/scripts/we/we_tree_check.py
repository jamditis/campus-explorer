import bpy, json, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
foot=[n for n in bpy.data.objects.keys() if n.startswith(('WD_Bohn_N','WD_walk_','TK_Bohn_landing'))]
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); m.transform(o.matrix_world)
    t=BVHTree.FromPolygons([v.co.copy() for v in m.vertices],[list(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return t
fb={n:bvh(bpy.data.objects[n]) for n in foot}
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
def gz(x,y):
    r=sk.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return round(r[1].z,2) if r[0] else None
out=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree_'): continue
    p=o.matrix_world.translation
    if (p.xy-Vector((226.8,413.4))).length>14: continue
    # trunk: lowest-3m verts near origin
    e=o.evaluated_get(dg); m=e.to_mesh()
    tv=[o.matrix_world@v.co for v in m.vertices if (o.matrix_world@v.co).z<p.z+2.5]
    e.to_mesh_clear()
    md=1e9; mdn=None
    for n,t in fb.items():
        for q in tv[::max(1,len(tv)//60)] or [p]:
            r=t.find_nearest(q)
            if r[0] is not None and r[3]<md: md=r[3]; mdn=n
    out.append(dict(name=o.name,loc=[round(x,2) for x in p],ground=gz(p.x,p.y),trunk_nv=len(tv),min_dist_lower=round(md,2),nearest=mdn,data=o.data.name,users=o.data.users))
print(json.dumps(out,indent=0))
json.dump(out,open('data/we/tree_check.json','w'),indent=1)

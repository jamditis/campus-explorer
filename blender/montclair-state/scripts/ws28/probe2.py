import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    ev=o.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); ev.to_mesh_clear(); return t
road=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; RB=bvh(road)
# objects whose bbox overlaps road area
xs=(-250,-196); ys=(-162,-50)
cand=[]
for o in sc.objects:
    if o.type not in('MESH',) or o.hide_render: continue
    if o.name.startswith('T_') or o.name.startswith('WS27'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(b.x for b in bb)<xs[0] or min(b.x for b in bb)>xs[1] or max(b.y for b in bb)<ys[0] or min(b.y for b in bb)>ys[1]: continue
    cand.append(o)
print('cands',len(cand))
res=[]
for o in cand:
    try:
        ev=o.evaluated_get(dg); me=ev.to_mesh()
    except Exception as e: continue
    mw=o.matrix_world; n=0; mx=0; ex=[]
    for v in me.vertices:
        p=mw@v.co
        if not(xs[0]<p.x<xs[1] and ys[0]<p.y<ys[1]): continue
        h=RB.ray_cast(Vector((p.x,p.y,p.z+5)),Vector((0,0,-1)),10)
        if h[0] and p.z>h[0].z+0.005 and p.z<h[0].z+3:
            n+=1; d=p.z-h[0].z
            if d>mx: mx=d
            if len(ex)<4: ex.append((round(p.x,1),round(p.y,1),round(d,2)))
    ev.to_mesh_clear()
    if n: res.append((n,o.name,round(mx,2),ex))
res.sort(reverse=True)
for r in res[:30]: print(r)

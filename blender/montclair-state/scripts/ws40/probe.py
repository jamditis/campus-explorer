import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-225,-170,-125,-60
T={}
for o in sc.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if max(xs)-min(xs)<300:
        print('P40 obj %-60s x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(o.name[:60],min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)))
    if o.name.startswith('T_'): continue
    try:
        e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if not (X0<v.co.x<X1 and Y0<v.co.y<Y1)],context='VERTS')
        if len(bm.faces): T[o.name]=BVHTree.FromBMesh(bm)
        bm.free(); e.to_mesh_clear()
    except Exception as ex: print('P40 err',o.name,ex)
def stack(x,y):
    out=[]
    for n,t in T.items():
        z=300
        for k in range(3):
            r=t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),400)
            if not r[0]: break
            out.append((n[:30],round(r[0].z,2))); z=r[0].z-0.005
    return sorted(out,key=lambda a:-a[1])[:4]
for y in (-100,-94,-90,-86,-80):
    for x in range(-212,-176,2):
        print('P40 stack',x,y,stack(x,y))

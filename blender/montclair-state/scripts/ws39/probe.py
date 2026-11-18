import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-232,-188,-112,-74
T={}
for o in sc.objects:
    if o.type!='MESH' or o.hide_render or o.hide_get(): continue
    if o.name.startswith('T_') or 'RedHawk' in o.name: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
    if (max(p.x for p in bb)-min(p.x for p in bb))>800: pass
    try:
        e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
        # crop
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if not (X0-5<v.co.x<X1+5 and Y0-5<v.co.y<Y1+5)],context='VERTS')
        if len(bm.faces): T[o.name]=BVHTree.FromBMesh(bm)
        bm.free(); e.to_mesh_clear()
    except Exception as ex: print('P39 err',o.name,ex)
print('P39 objs',len(T),sorted(T)[:80])
def cast(o,d):
    best=None
    for n,t in T.items():
        r=t.ray_cast(o,d,400)
        if r[0] and (best is None or r[3]<best[2]): best=(n,r[0],r[3])
    return best
cam=bpy.data.objects['WS35_CAM_eye_Kasser_steps_from_CollegeAve_SW']
sc.render.resolution_x=960; sc.render.resolution_y=540
tr,br,bl,tl=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]; o=cam.matrix_world.translation
print('P39 cam',[round(c,2) for c in o])
for px in range(60,960,60):
    for py in range(240,352,6):
        u=px/960; v=py/540; p=(tl+(tr-tl)*u)+((bl+(br-bl)*u)-(tl+(tr-tl)*u))*v
        b=cast(o,(p-o).normalized())
        print('P39 px',px,py,(b[0],tuple(round(c,2) for c in b[1])) if b else None)
def stack(x,y):
    out=[]
    for n,t in T.items():
        z=300
        for k in range(3):
            r=t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),400)
            if not r[0]: break
            out.append((n[:34],round(r[0].z,2))); z=r[0].z-0.005
    return sorted(out,key=lambda a:-a[1])
for y in range(-100,-82,2):
    for x in (-204,-203,-202.4,-202,-201,-200):
        print('P39 stack',x,y,stack(x,y))

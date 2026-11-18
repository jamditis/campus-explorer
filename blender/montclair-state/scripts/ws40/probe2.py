import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws40/render40.py').read().split("base=bpy.data.objects.get('Sun')")[0].replace("SX,SY=float(os.environ['SX']),float(os.environ['SY'])","SX,SY=-175,-112"))
X0,X1,Y0,Y1=-202,-186,-106,-90; T={}
for o in sc.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not (X0<v.co.x<X1 and Y0<v.co.y<Y1)],context='VERTS')
    if len(bm.faces): T[o.name]=BVHTree.FromBMesh(bm)
    bm.free(); e.to_mesh_clear()
bpy.context.view_layer.update(); print("P40b nT",len(T),sorted(T)); cam=bpy.data.objects["WS40_CAM_closeup_steps_foot_sidewalk"]; print("P40b cam",tuple(cam.location)); sc.render.resolution_x=960; sc.render.resolution_y=540
tr,br,bl,tl=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]; o=cam.matrix_world.translation
for px,py in [(330,390),(300,370),(250,330),(420,460),(380,420),(260,300),(240,250),(450,520),(350,500)]:
    u=px/960; v=py/540; p=(tl+(tr-tl)*u)+((bl+(br-bl)*u)-(tl+(tr-tl)*u))*v; d=(p-o).normalized(); best=None
    for n,t in T.items():
        r=t.ray_cast(o,d,200)
        if r[0] and (best is None or r[3]<best[2]): best=(n,r[0],r[3])
    print('P40b',px,py,best[0] if best else None, tuple(round(c,2) for c in best[1]) if best else None)

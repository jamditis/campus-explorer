import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
names=['Susan A. Cole Hall walls','TZ_Cole_windows_EN_UNVERIFIED','TZ_Cole_north_addition_UNVERIFIED','TW_Cole_windows_SW_UNVERIFIED','WS6_Cole_gable_arched_window_UNVERIFIED','WS7_Cole_gable_base_course_UNVERIFIED']
trees={}
for n in names:
    o=bpy.data.objects[n]
    if o.hide_render: continue
    bm=__import__('bmesh').new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    trees[n]=(BVHTree.FromBMesh(bm),bm)
cam=Vector((-68.6,-68.9,136.15)); tgt=Vector((-84.5,-64.4,135.0))
d0=(tgt-cam); a0=math.atan2(d0.y,d0.x)
for da in [5,10,15,20,25,30]:
  for dz in [0.0,0.1]:
    a=a0+math.radians(da); d=Vector((math.cos(a),math.sin(a),dz)).normalized()
    best=None
    for n,(t,bm) in trees.items():
        h=t.ray_cast(cam,d,300)
        if h[0] is not None and (best is None or h[3]<best[3]): best=(n,h[0],h[1],h[3],h[2])
    if best:
        n,p,nm,dist,idx=best
        print('HIT',da,dz,n,[round(v,2) for v in p],[round(v,2) for v in nm],round(dist,1))
# walls faces list near
o=bpy.data.objects['Susan A. Cole Hall walls']
for p in o.data.polygons:
    c=o.matrix_world@p.center
    if c.x>-100 and c.y>-90 and abs(p.normal.z)<0.5:
        print('W',[round(v,2) for v in c],[round(v,2) for v in p.normal],round(p.area,1),o.material_slots[p.material_index].material.name)

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; cam=bpy.data.objects['QL_CAM_closeup_ccis_east_S_junction']; sc.camera=cam
sc.render.resolution_x=1024; sc.render.resolution_y=576
dg=bpy.context.evaluated_depsgraph_get(); M=cam.matrix_world; o=M.translation
tr,br,bl,tl=[M@v for v in cam.data.view_frame(scene=sc)]
cands=[]
for ob in sc.objects:
    if ob.type!='MESH' or ob.hide_render: continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    if min(p.x for p in bb)<46 and max(p.x for p in bb)>24 and min(p.y for p in bb)<215 and max(p.y for p in bb)>190 and max(ob.dimensions)<300:
        cands.append((ob,BVHTree.FromObject(ob,dg)))
print('CANDS',len(cands))
for px,py in [(470,430),(490,470),(510,520),(530,560),(480,540),(440,500),(620,560)]:
    u=px/1024;v=py/576; p=tl.lerp(tr,u).lerp(bl.lerp(br,u),v); d=(p-o).normalized()
    best=None
    for ob,b in cands:
        mw=ob.matrix_world; mi=mw.inverted(); lo=mi@o; ld=(mi.to_3x3()@d).normalized()
        h=b.ray_cast(lo,ld)
        if h[0] is not None:
            w=mw@h[0]; dist=(w-o).length
            if best is None or dist<best[0]: best=(dist,ob.name,tuple(round(a,2) for a in w),tuple(round(a,2) for a in (mw.to_3x3()@h[1]).normalized()),h[2])
    print('PX',px,py,best)

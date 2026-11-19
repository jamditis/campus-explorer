import bpy
from mathutils import Vector
o=bpy.data.objects['T_SugarMaple_L1_0281']; M=o.matrix_world
bb=[M@Vector(c) for c in o.bound_box]
print('P224 loc',tuple(round(c,3) for c in o.location),'parent',o.parent.name if o.parent else None,'bbz %.3f..%.3f'%(min(v.z for v in bb),max(v.z for v in bb)),'data',o.data.name,o.data.users,'scale',tuple(o.scale))
# lowest vertices (trunk base) xy
vs=sorted((M@v.co for v in o.data.vertices),key=lambda w:w.z)[:20]
cx=sum(w.x for w in vs)/20; cy=sum(w.y for w in vs)/20
print('P224 trunk base ~(%.2f,%.2f) z %.3f'%(cx,cy,vs[0].z))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
z=160
for _ in range(10):
    h,loc,n,i,ob,m=sc.ray_cast(dg,Vector((cx,cy,z)),Vector((0,0,-1)))
    if not h: break
    print('P224 hit',ob.name[:50],'%.3f'%loc.z); z=loc.z-0.01
# other objects sharing the mesh: their bottoms vs ground, sample 10

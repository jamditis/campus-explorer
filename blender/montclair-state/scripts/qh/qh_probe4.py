import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bvh=BVHTree.FromObject(T,dg)
sc=bpy.context.scene
for o in bpy.data.objects:
    if (o.name.startswith('Lamp_acorn') or o.name.startswith('Bench_walk')) and not o.hide_render:
        x,y,z=o.matrix_world.translation
        if y<140: continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zmin=min(v.z for v in bb)
        t=bvh.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        o.hide_set(True) if False else None
        r=sc.ray_cast(dg,Vector((x+1.2,y+1.2,400)),Vector((0,0,-1)))
        print('L',o.name,round(zmin,2),'terr',None if t is None else round(t.z,2),'near',round(r[1].z,2),r[4].name if r[0] else None)
for nm in ('PC_fillet_grass_points_UNVERIFIED','PL_feliciano_lawn_grass_points_UNVERIFIED'):
    o=bpy.data.objects[nm]; MW=o.matrix_world; d=[]
    for v in o.data.vertices:
        p=MW@v.co
        if p.y<140: continue
        t=bvh.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))[0]
        if t is not None: d.append(p.z-t.z)
    d=np.array(d); print('PTS',nm,len(o.data.vertices),len(d),'p1/50/99',np.percentile(d,[1,5,50,95,99]).round(2),'|d|>0.3',(abs(d)>0.3).sum(),'>1',(abs(d)>1).sum())

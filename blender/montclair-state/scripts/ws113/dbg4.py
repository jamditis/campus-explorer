import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; px=bpy.data.objects['WS113_paving_tops_proxy']
b=next(o for o in bpy.data.objects if o.name.startswith('WS112_CollegeAve_S_E_walk_N_brick'))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
me=t.evaluated_get(dg).data
seen=set()
for p in b.data.polygons:
    if p.normal.z<0.5: continue
    q=b.matrix_world@p.center
    h=sc.ray_cast(dg,q+Vector((0,0,3)),Vector((0,0,-1)),distance=3.05)
    if h[0] and h[4].name.startswith('Terrain') and h[3] not in seen:
        seen.add(h[3]); f=me.polygons[h[3]]; vs=[me.vertices[i].co for i in f.vertices]
        print('P113 face',h[3],'nv',len(vs),'hit z %.3f walk z %.3f'%(h[1].z,q.z),' '.join('(%.2f,%.2f,%.2f)'%tuple(v) for v in vs))

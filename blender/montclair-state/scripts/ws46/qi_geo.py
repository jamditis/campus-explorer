import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=['QI_east_edge_LiDAR_terrain_patch','QI_east_edge_delete_probe']
D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
Ts={}
for o in to.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    print('QG',o.name,len(o.data.vertices),len(o.data.polygons),[round(f(p[i] for p in bb),1) for i in range(3) for f in (min,max)], 'hide_render',o.hide_render)
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); Ts[o.name]=BVHTree.FromBMesh(bm)
P=Ts['QI_east_edge_LiDAR_terrain_patch']; Q=Ts['QI_east_edge_delete_probe']
for y in range(-58,-80,-2):
    row=[]
    for x in range(92,142,4):
        p=P.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]; q=Q.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
        d=D[int(y+250),int(x+250)]
        row.append(('P%+.1f'%(p.z-d) if p else ' P---')+('q' if q else '.'))
    print('QR',y,' '.join(row))

import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to): to.collections=['Terrain']
col=to.collections[0]; bpy.context.scene.collection.children.link(col)
print('SW2 objs',len(col.all_objects),[o.name for o in col.all_objects][:40])
D=np.load('data/dtm_1m.npy'); dg=bpy.context.evaluated_depsgraph_get(); dg.update()
Ts=[]
for o in col.all_objects:
    if o.type!='MESH' or o.hide_render: continue
    m=o.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); Ts.append((o.name,BVHTree.FromBMesh(bm),m)); bm.free()
R=[]
for y in range(-246,247,4):
    for x in range(-246,247,4):
        best=None
        for n,T,m in Ts:
            h,nn,i,d=T.ray_cast(Vector((x,y,500)),Vector((0,0,-1)),1000)
            if h and (best is None or h.z>best[0]): best=(h.z,m.polygons[i].area if n=='Terrain_LiDAR_DTM_1m' else 0,n)
        if best: R.append((x,y,best[0]-D[y+250,x+250],best[1]))
R=np.array(R); np.save('data/ws64_sweep2.npy',R); print('SW2',len(R),'|d|>1',int((np.abs(R[:,2])>1).sum()))

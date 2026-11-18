import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m'];dg=bpy.context.evaluated_depsgraph_get()
m=T.evaluated_get(dg).to_mesh();bm=bmesh.new();bm.from_mesh(m);bm.transform(T.matrix_world);BV=BVHTree.FromBMesh(bm)
D=np.load('data/dtm_1m.npy')
print('P86 cams',[o.name for o in bpy.data.objects if o.type=='CAMERA' and ('WS8' in o.name or 'ws8' in o.name)])
rows=[]
for y in range(-150,-99,2):
    r=[]
    for x in range(-260,-199,2):
        h=BV.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)
        r.append(round(h[0].z-D[y+250,max(x,-250)+250],1) if h[0] else 99)
        if h[0] and abs(h[1].z)<0.985: r[-1]=str(r[-1])+'*'
    rows.append((y,r))
print('P86 dz terrain-DTM  x -260..-200 step 2 ( * = tilt>10deg )')
for y,r in rows: print('P86 y%d'%y,' '.join(str(v).rjust(5) for v in r))
# hit object at top surface (what renders) along same grid
dg2=dg;sc=bpy.context.scene

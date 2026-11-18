import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    to.objects=[n for n in fr.objects if (n.startswith('Terrain_LiDAR') or n.startswith('QI_east_edge_LiDAR') or n.startswith('WS50_') or n.startswith('WS47') or n.startswith('WS60_terrain'))]
D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
dg=bpy.context.evaluated_depsgraph_get()
for o in to.objects: bpy.context.scene.collection.objects.link(o)
dg.update(); Ts=[]
for o in to.objects:
    if o.type!='MESH' or o.hide_render: continue
    m=o.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); Ts.append((o.name,BVHTree.FromBMesh(bm)))
print('BP objs',[n for n,_ in Ts])
for y in range(-54,-84,-2):
    row=[]
    for x in range(88,142,3):
        best=None
        for n,T in Ts:
            h=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
            if h and (best is None or h.z>best): best=h.z
        d=D[int(y+250),int(x+250)]
        row.append('%+5.1f'%(best-d) if best else '  ---')
    print('BR%4d'%y,' '.join(row))
print('BX',' '.join('%5d'%x for x in range(88,142,3)))

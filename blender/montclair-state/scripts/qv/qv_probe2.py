import bpy,numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
g=np.load('north/data/grid_1m.npz'); D=g['dtm_filled']
S=bpy.data.objects['Context_skirt_3DEP_ortho_4km'];es=S.evaluated_get(dg);iws=S.matrix_world.inverted()
d=[]
for y in range(250,345,5):
    row=''
    for x in range(10,160,5):
        r=es.ray_cast(iws@Vector((x,y,400)),Vector((0,0,-1)))
        if not r[0]: row+='   .'; continue
        z=(S.matrix_world@r[1]).z; l=float(D[int(y+260),int(x+600)]); d.append(z-l); row+='%4d'%round((z-l)*10)
    print('DZ y=%d'%y,row)
d=np.array(d); print('DZSTAT',d.mean(),d.std(),np.abs(d).max())
for n in ('Ground_ortho_grass','Lawn_Varied_Oct_local_fade'):
    m=bpy.data.materials[n]
    print('MAT',n,[(nd.name,nd.image.name,nd.image.size[:]) for nd in m.node_tree.nodes if nd.type=='TEX_IMAGE' and nd.image])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('TUV',[u.name for u in T.data.uv_layers])
print('SKUV',[u.name for u in S.data.uv_layers])

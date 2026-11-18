"""we: probe the 5 remaining 22 cm QT soil strips: bbox, verts, terrain-like meshes overlapping their bbox."""
import bpy,numpy as np
from mathutils import Vector
O=bpy.data.objects
IDS=('313027428','313027430','313027432','313027437','546643369')
names=[k for k in O.keys() if k.startswith('QT_soil_edge_') and any(t in k for t in IDS)]
print('NAMES',names,flush=True)
def bb(o):
    c=np.array([o.matrix_world@Vector(b) for b in o.bound_box]); return c[:,0].min(),c[:,0].max(),c[:,1].min(),c[:,1].max(),c[:,2].min(),c[:,2].max()
TERR=[o for o in O if o.type=='MESH' and len(o.data.polygons)>200 and any(k in o.name for k in ('LiDAR','DTM','RZ','Terrain','skirt','lawn','Lawn','ground','Ground','grass_base'))]
print('TERR',len(TERR),flush=True)
for n in names:
    t=O[n]; b=bb(t)
    ov=[]
    for o in TERR:
        c=bb(o)
        if c[0]<b[1] and c[1]>b[0] and c[2]<b[3] and c[3]>b[2]: ov.append(o.name)
    print('STRIP',n,len(t.data.vertices),[round(x,1) for x in b],'OV',ov,flush=True)

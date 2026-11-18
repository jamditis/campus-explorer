import bpy, math, numpy as np
from mathutils import Vector
g=np.load('north/data/grid_1m.npz'); D=g['dtm_filled']
def gz(x,y): return float(D[int(math.floor(y+260)),int(math.floor(x+600))])
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
hide=[o for o in bpy.data.objects if o.name!='Terrain_LiDAR_DTM_1m' and o.type=='MESH']
for y in range(105,265,10):
    row=[]
    for x in range(-150,220,15):
        o=Vector((x,y,400)); z=None
        for _ in range(12):
            ok,loc,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
            if not ok: break
            if ob.name=='Terrain_LiDAR_DTM_1m': z=loc.z; break
            o=loc-Vector((0,0,0.01))
        row.append('%5.1f'%(z-gz(x,y)) if z is not None else '  -- ')
    print('Y%4d'%y,' '.join(row))

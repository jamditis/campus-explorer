import bpy, math, numpy as np
from mathutils import Vector
g=np.load('north/data/grid_1m.npz'); D=g['dtm_filled']
def gz(x,y): return float(D[int(math.floor(y+260)),int(math.floor(x+600))])
for nm in ('Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m'):
    T=bpy.data.objects[nm]; Mi=T.matrix_world.inverted(); print('OBJ',nm,[m.name for m in T.modifiers])
    for y in range(150,420,30):
        row=[]
        for x in range(-150,220,30):
            ok,loc,n,i=T.ray_cast(Mi@Vector((x,y,400)),(Mi.to_3x3()@Vector((0,0,-1))).normalized())
            row.append('%5.1f'%((T.matrix_world@loc).z-gz(x,y)) if ok else '  -- ')
        print('Y%4d'%y,' '.join(row))

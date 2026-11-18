import bpy, math, numpy as np
from mathutils import Vector
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('TMODS',[ (m.name,m.type,m.show_render) for m in T.modifiers], T.location[:], len(T.data.vertices))
import os
if os.environ.get("NOMOD"):
    [setattr(m,"show_viewport",False) for m in T.modifiers]
dg=bpy.context.evaluated_depsgraph_get(); Te=T.evaluated_get(dg); Mi=T.matrix_world.inverted()
g=np.load('north/data/grid_1m.npz'); D=g['dtm_filled']
def gz(x,y): return float(D[int(math.floor(y+260)),int(math.floor(x+600))])
def tz(x,y):
    ok,loc,n,i=Te.ray_cast(Mi@Vector((x,y,300)),(Mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else None
for y in range(105,265,10):
    row=[]
    for x in range(-150,220,15):
        t=tz(x,y); row.append('%5.1f'%(t-gz(x,y)) if t is not None else '  -- ')
    print('Y%4d'%y,' '.join(row))
for nm in ('CCOM','Morehead','Life'):
    pass

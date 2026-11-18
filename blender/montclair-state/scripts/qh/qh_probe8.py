import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
D=np.load('north/data/grid_1m.npz')['dtm_filled']
out=[]
for y in range(-30,248,12):
    row=[]
    for x in range(120,246,10):
        r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        l=float(D[int(y+260),int(min(x,219)+600)])
        n=r[4].name[:4] if r[0] else '----'
        row.append('%s%+.0f'%(n,(r[1].z-l) if r[0] else 0))
    print('R%4d '%y+' '.join('%9s'%c for c in row))

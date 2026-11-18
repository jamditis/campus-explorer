import bpy, math, numpy as np
from mathutils import Vector
ZS=np.load('/workspace/nj-scenes/montclair-state/scripts/ws162/dtm162.npy')[1]; X0,Y1,R=-330.0,-165.0,0.5
def dz(x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in np.arange(-230,-245.1,-1.5):
    row=[]
    for x in np.arange(-320,-299.9,2.0):
        r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
        row.append('%s%+.2f'%(r[4].name[:9] if r[0] else '-', (r[1].z-dz(x,y)) if r[0] else 0))
    print('PROBE y%.1f '%y+' '.join(row),flush=True)

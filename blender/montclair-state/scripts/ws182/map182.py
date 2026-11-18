# ws182 read-only: top-surface object map over the Lot 36 NE drive / service lane / bank-toe join (after fix181)
import numpy as np, bpy, os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,X1,Y0,Y1,ST=[float(v) for v in os.environ.get('WIN','-322,-310,-226,-206,0.2').split(',')]
codes={}
rows=[]
for y in np.arange(Y1,Y0-1e-6,-ST):
    r=''
    for x in np.arange(X0,X1+1e-6,ST):
        hit,loc,n,i,o,m=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1)))
        if not hit: r+=' '; continue
        k=o.name
        if k not in codes: codes[k]='ABCDEFGHIJKLMNOPQRSTUVWXYZ'[len(codes)]
        r+=codes[k]
    rows.append('%7.1f %s'%(y,r))
print('MAPLEGEND',codes); print('MAPX from %.1f step %.1f'%(X0,ST))
for r in rows: print('MAP',r)

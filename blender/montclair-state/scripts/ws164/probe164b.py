import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/probe164.py').read().split("dg=bpy.context")[0])
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164a.py').read())
bpy.context.view_layer.update()
exec("dg=bpy.context"+open('/workspace/nj-scenes/montclair-state/scripts/ws164/probe164.py').read().split("dg=bpy.context",1)[1])
# zone grid check
from collections import Counter
C=Counter(); bad=[]
import numpy as np
for x in np.arange(-303,-266,0.5):
    for y in np.arange(-262,-236,0.5):
        r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
        if r[0]:
            C[r[4].name[:40]]+=1
            if r[2].z<0.85 or r[4].name.startswith(('Context','Terrain','WS113')): bad.append((x,y,r[4].name[:30],round(r[1].z,2),round(r[2].z,2)))
print('ZONE',C.most_common()); print('BAD',len(bad),bad[:30])

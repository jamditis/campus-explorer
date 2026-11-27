# ws259 W64 (FULL main, no save): 1 m grid x -292..-232, y -246..-196 — top non-tree surface; cells whose top is the skirt/floor = missing ground
import bpy, json, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
Z=np.load('/workspace/nj-scenes/montclair-state/prep/ws259_w64/dtm259.npy')[0]
X0,Y0=-292.,-246.; out=[]
for j in range(Z.shape[0]):
    for i in range(Z.shape[1]):
        x,y=X0+i+0.5,Y0+j+0.5; o0=Vector((x,y,250)); nm=None; z=None
        for k in range(8):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            n=r[4].name
            if n.startswith(('T_','TREE','Tree','Lamp')) or 'leaf' in n.lower() or 'canopy' in n.lower(): o0=r[1]+Vector((0,0,-0.001)); continue
            nm,z=n,r[1].z; break
        out.append((i,j,nm,z,float(Z[j,i])))
json.dump(out,open('/workspace/nj-scenes/montclair-state/prep/ws259_w64/top259.json','w'))
from collections import Counter
miss=[o for o in out if o[2] is None or o[2].startswith(('Context_skirt','Context_ground'))]
print('P259H cells',len(out),'skirt/none top',len(miss),Counter(o[2][:30] if o[2] else None for o in out).most_common(12),flush=True)
d=[o[4]-o[3] for o in miss if o[3] is not None]
print('P259H LiDAR - skirt on missing cells p10/50/90 %.2f %.2f %.2f'%tuple(np.percentile(d,[10,50,90])),flush=True)

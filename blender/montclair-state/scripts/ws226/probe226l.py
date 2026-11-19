import bpy, sys, os, json
from mathutils import Vector
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
D=np.load('/workspace/nj-scenes/montclair-state/data/skirt_dem_10m.npy')
def ref(x,y):
    if y>185 and x>125: return float(D[int((2000-y)/10), int((x+2000)/10)])
    return float(A[min(499,int(y+250)),min(499,int(x+250))])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
# base faces in the east: long ones
out=[]
for p in me.polygons:
    c=p.center
    if c.x<60: continue
    vs=[me.vertices[i].co for i in p.vertices]
    L=max((vs[i]-vs[i-1]).length for i in range(len(vs)))
    hi=c.z-ref(c.x,c.y)
    if L>20 and abs(hi)>1.0:
        out.append((p.index,round(p.area,1),round(L,1),round(c.x,1),round(c.y,1),round(hi,2),[tuple(round(q,1) for q in v) for v in vs][:6]))
print('P226L long east base faces off ref >1m',len(out),flush=True)
for r in sorted(out,key=lambda r:-r[2])[:30]: print('P226L',r,flush=True)
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226l.json','w'))
sys.stdout.flush(); os._exit(0)

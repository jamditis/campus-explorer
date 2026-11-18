import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
X0,X1,Y0,Y1,ST=map(float,os.environ['BOX'].split(','))
import json
BB=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
want=[n for n,(t,hr,x0,x1,y0,y1,z0,z1,c) in BB.items() if t=='MESH' and not hr and not n.startswith(('Context_skirt','BD_farfield')) and not (x1<X0 or x0>X1 or y1<Y0 or y0>Y1) and z1<145]
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in want if n in set(a.objects)]
T={}
for o in b.objects:
    if o is None or o.type!='MESH' or len(o.data.polygons)==0: continue
    me=o.data; mw=o.matrix_world
    T[o.name]=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def hits(x,y):
    r=[]
    for n,t in T.items():
        h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80)
        if h[0] is not None: r.append((h[0].z,n))
    return sorted(r,reverse=True)
L={}; Z=[]
for y in np.arange(Y1,Y0-1e-6,-ST):
    row=''; zr=[]
    for x in np.arange(X0,X1+1e-6,ST):
        r=hits(x,y); n=r[0][1] if r else '-'
        L.setdefault(n,chr(65+len(L)) if len(L)<26 else chr(97+len(L)-26)); row+=L[n]; zr.append(r[0][0] if r else np.nan)
    Z.append(zr); print('M206 %7.2f %s'%(y,row))
for n,c in L.items(): print('M206',c,n)
Z=np.array(Z); np.save('/tmp/m206z.npy',Z)
if os.environ.get('ZP'):
  for y in np.arange(Y1,Y0-1e-6,-ST*2):
    print('M206z %6.1f '%y+' '.join('%.2f'%hits(x,y)[0][0] if hits(x,y) else ' -- ' for x in np.arange(X0,X1+1e-6,ST*2)))

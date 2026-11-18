import bpy, json, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
x0,x1,y0,y1=map(float,os.environ['BOX'].split(','))
want=[n for n,v in B.items() if v[0]=='MESH' and not v[1] and not n.startswith(('Context_skirt','BD_farfield')) and not (v[3]<x0 or v[2]>x1 or v[5]<y0 or v[4]>y1) and v[6]<150]
with bpy.data.libraries.load(os.environ['PF']) as (a,b): b.objects=[n for n in want if n in set(a.objects)]
T={}
for o in b.objects:
    if o.type!='MESH' or not len(o.data.polygons): continue
    mw=o.matrix_world; T[o.name]=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
st=float(os.environ.get('STEP','1')); out={}
for y in np.arange(y1,y0-1e-6,-st):
    for x in np.arange(x0,x1+1e-6,st):
        hs=[]
        for n,t in T.items():
            h=t.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),60)
            if h[0] is not None: hs.append((round(h[0].z,3),n))
        hs.sort(reverse=True); out['%.2f,%.2f'%(x,y)]=hs[:4]
json.dump(out,open(os.environ['OUTJ'],'w')); print('PB209',len(T),flush=True)
for n in sorted(T): print('OBJ',n)

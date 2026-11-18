# ws208 top-object/z probe over BOX (x0,x1,y0,y1) at STEP using base meshes (modifiers off); writes OUTJ json
import bpy, os, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S='/workspace/nj-scenes/montclair-state/scripts/'
B=json.load(open(S+'ws205/bbox205.json'))
x0,x1,y0,y1=map(float,os.environ['BOX'].split(',')); st=float(os.environ.get('STEP','1'))
ZMAX=float(os.environ.get('ZMAX','1e9'))
want=[n for n,v in B.items() if v[0]=='MESH' and not v[1] and not n.startswith(('Context_skirt','BD_farfield')) and not (v[3]<x0 or v[2]>x1 or v[5]<y0 or v[4]>y1) and v[6]<ZMAX]
with bpy.data.libraries.load(os.environ.get('FILE','/workspace/nj-scenes/montclair-state/montclair_state.blend')) as (a,b):
    b.objects=[n for n in want if n in set(a.objects)]
T={}
for o in b.objects:
    if o is None or o.type!='MESH' or not o.data.polygons: continue
    mw=o.matrix_world; T[o.name]=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
xs=np.arange(x0,x1+1e-6,st); ys=np.arange(y1,y0-1e-6,-st)
G=[];L={}
for y in ys:
    row=[]
    for x in xs:
        best=None
        for n,t in T.items():
            h=t.ray_cast(Vector((x,y,ZMAX if ZMAX<1e8 else 400)),Vector((0,0,-1)),500)
            if h[0] is not None and (best is None or h[0].z>best[1]): best=(n,h[0].z)
        row.append(best); 
        if best: L.setdefault(best[0],len(L))
    G.append(row)
json.dump({'xs':list(map(float,xs)),'ys':list(map(float,ys)),'G':G},open(os.environ['OUTJ'],'w'))
print('P208',len(T),'objs',len(L),'tops',flush=True)
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM208',l.strip(),flush=True)

import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=os.environ['PF'].split('|')
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(tuple(PF))]
T={}
for o in b.objects:
    me=o.data; mw=o.matrix_world
    T[o.name[:14]]=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
print('P206 keys',list(T))
for y in [float(v) for v in os.environ['YS'].split(',')]:
    x0,x1=map(float,os.environ['XR'].split(','))
    for x in np.arange(x0,x1+1e-6,0.1):
        s=' '.join('%s=%s'%(k[:6],'%.3f'%hz(t,x,y) if hz(t,x,y) is not None else '  -  ') for k,t in T.items())
        print('P206 y%.1f x%.2f %s'%(y,x,s))

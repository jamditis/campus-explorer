import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=('WS98_','WS99_lotE_padS_bed','WS27_CollegeAve','Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS73')
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
T={}
for o in b.objects:
    if o.type!='MESH': continue
    me=o.data; mw=o.matrix_world
    T[o.name]=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def top(x,y):
    best=None
    for n,t in T.items():
        h=t.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),60)
        if h[0] is not None and (best is None or h[0].z>best[1]): best=(n,h[0].z)
    return best
L={}
for y in np.arange(-82,-96,-0.5):
    row=''
    for x in np.arange(-212,-196,0.5):
        r=top(x,y); n=r[0] if r else '-'
        L.setdefault(n,chr(97+len(L))); row+=L[n]
    print('M205 %6.1f %s'%(y,row))
print('M205',L)
# z profile of aisle: residual vs smooth
A=[o for o in b.objects if o.name.startswith('WS98_lotE_entry_aisle')][0]
P=np.array([tuple(A.matrix_world@v.co) for v in A.data.vertices])
res=[]
for p in P:
    d2=((P[:,:2]-p[:2])**2).sum(1); w=np.exp(-d2/(2*2.0**2))
    X=np.c_[np.ones(len(P)),P[:,0]-p[0],P[:,1]-p[1]]
    W=np.sqrt(w)[:,None]; c=np.linalg.lstsq(X*W,P[:,2]*W[:,0],rcond=None)[0]; res.append(p[2]-c[0])
res=np.array(res); print('M205 aisle bbox',P.min(0),P.max(0),'resid rms %.3f max %.3f'%(np.sqrt((res**2).mean()),abs(res).max()))
for y in np.arange(-82,-94,-1):
    print('M205 z',y,' '.join('%s'%('%.2f'%top(x,y)[1] if top(x,y) else '----') for x in np.arange(-210,-197,1)))

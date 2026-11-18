import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
X0,X1,Y0,Y1=-236,-204,-198,-158
dg=bpy.context.evaluated_depsgraph_get()
T=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if o.name.startswith(('T_','WS108_win','WS107_Chapin')) : continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    if len(me.polygons)==0: e.to_mesh_clear(); continue
    mats=[m.name if m else '-' for m in o.data.materials]
    T.append((o.name,BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]),[mats[p.material_index] if p.material_index<len(mats) else '-' for p in me.polygons]))
    print('OBJ',o.name,len(me.polygons),[m[:30] for m in mats][:4]); e.to_mesh_clear()
import collections
rows=[]
for y in np.arange(-196,-159.9,1.0):
  line=[]
  for x in np.arange(-216,-204.9,0.5):
    best=None
    for nm,b,mt in T:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if h[0] is not None and (best is None or h[0].z>best[0]): best=(h[0].z,nm,mt[h[2]])
    if best: line.append('%s%+.1f'%(best[1][:6],best[0]-dtm(x,y)))
  print('Y',y,' '.join(line))
# top-object/material census
cnt=collections.Counter()
for y in np.arange(-196,-160,0.5):
  for x in np.arange(-216,-205,0.5):
    best=None
    for nm,b,mt in T:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if h[0] is not None and (best is None or h[0].z>best[0]): best=(h[0].z,nm,mt[h[2]])
    if best: cnt[(best[1][:40],best[2][:30])]+=1
for k,v in cnt.most_common(): print('TOP',v,k)

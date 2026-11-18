import bpy, numpy as np
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
dg=bpy.context.evaluated_depsgraph_get()
def objs_in(x0,x1,y0,y1):
    out=[]
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
        if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: continue
        out.append(o)
    return out
print('P DTM grid #24')
for y in range(-176,-153,2):
    print('P y',y,' '.join('%.2f'%dtm(x,y) for x in range(-224,-200,2)))
print('P DTM #25')
for y in np.arange(-206,-199,1.0):
    print('P y',y,' '.join('%.2f'%dtm(x,y) for x in np.arange(-216,-204,1.0)))
# top hit per point with object name
cands=objs_in(-226,-200,-210,-150)
from mathutils.bvhtree import BVHTree
bv={}
for o in cands:
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    if len(me.polygons)==0: e.to_mesh_clear(); continue
    bv[o.name]=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear()
def hits(x,y):
    r=[]
    for n,b in bv.items():
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if h[0] is not None: r.append((round(h[0].z,2),n[:38]))
    return sorted(r,reverse=True)[:3]
for (x,y) in [(-218,-170),(-215,-170),(-212,-170),(-209,-170),(-206,-170),(-215,-167),(-209,-167),(-206,-166),(-212,-162),(-216,-160),(-209,-160),(-205,-174),(-212,-175),(-218,-176),
              (-212,-202),(-211,-202.5),(-210,-202.5),(-209.5,-203),(-211,-204),(-213,-204),(-210,-205)]:
    print('P hit',x,y,'dtm %.2f'%dtm(x,y),hits(x,y))
for o in cands:
    if any(k in o.name for k in ('door','Door','WS117','WS119','WS116')): 
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('P obj',o.name,[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])

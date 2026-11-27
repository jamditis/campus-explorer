# ws260 W64 probe (merge208 CHAIN, modifiers OFF = base meshes, no save): which objects cover each 1 m cell W of the WS103 walk
# x -268..-240, y -240..-194 (downward rays on per-object BVHs of world-space polygons inside the box). Prints a map + JSON.
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-268.0,-240.0,-240.0,-194.0
SKIP=('T_','TREE','Context_skirt','Context_ground_beyond','Roof_vent','el roof','Sky','Cloud')
cov={}
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(SKIP) or o.hide_render: continue
    mw=o.matrix_world; bb=[mw@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    me=o.data; V=[mw@v.co for v in me.vertices]; P=[]
    for p in me.polygons:
        vs=[V[i] for i in p.vertices]
        if max(v.x for v in vs)<X0 or min(v.x for v in vs)>X1 or max(v.y for v in vs)<Y0 or min(v.y for v in vs)>Y1: continue
        P.append(tuple(p.vertices))
    if not P: continue
    objs.append((o.name,BVHTree.FromPolygons(V,P)))
print('P260A objects',len(objs),[n[:30] for n,_ in objs],flush=True)
for j in range(int(Y1-Y0)):
    for i in range(int(X1-X0)):
        x=X0+i+0.5; y=Y0+j+0.5; hs=[]
        for n,t in objs:
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            if h[0] is not None: hs.append((n,round(h[0].z,2)))
        cov['%d,%d'%(i,j)]=hs
json.dump({'X0':X0,'Y0':Y0,'cov':cov},open('/workspace/nj-scenes/montclair-state/scripts/ws260/cov260a.json','w'))
print('P260A done',flush=True)
raise SystemExit

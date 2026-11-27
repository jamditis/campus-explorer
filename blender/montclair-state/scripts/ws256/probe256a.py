# ws256 read-only probe: Footpaths_OSM near Feliciano E walk N end (x -200..-180, y 186..206): base vs evaluated, vs terrain and ws253/255 walk
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ['F']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','WS250_W63','WS251_W63','WS253_W63','WS254_W63','WS255_W63','Footpaths_OSM','PI_Feliciano'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
print('P256 objs',[o.name for o in b.objects],flush=True)
fp=bpy.data.objects['Footpaths_OSM']
print('P256 FPmods',[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name, m.show_render) for m in fp.modifiers])
dg=bpy.context.evaluated_depsgraph_get()
BOX=(-202,-178,184,208)
def mesh(o,ev=True):
    em=(o.evaluated_get(dg) if ev else o).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(BOX[0]<vs[i].x<BOX[1] and BOX[2]<vs[i].y<BOX[3] for i in p.vertices)]
    return vs,ps
def bvh(o,ev=True):
    vs,ps=mesh(o,ev); return BVHTree.FromPolygons(vs,ps) if ps else None
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
W={o.name:bvh(o) for o in b.objects if o.name.startswith('WS25') and o.type=='MESH'}
W={k:v for k,v in W.items() if v}
print('P256 walks in box',list(W))
vs,ps=mesh(fp,True); vb,pb=mesh(fp,False)
print('P256 FP eval polys',len(ps),'base polys',len(pb))
used=sorted({i for p in ps for i in p})
for i in used: 
    v=vs[i]
    if BOX[0]<v.x<BOX[1] and BOX[2]<v.y<BOX[3]: pass
FPb=BVHTree.FromPolygons(vs,ps)
def top(bt,x,y):
    if bt is None: return float('nan')
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else float('nan')
print('P256 grid: x cols; each = FP z / terrain z / max walk z')
xs=np.arange(-197,-181,1.0)
print('P256 xs',list(xs))
for y in np.arange(186,206.1,1.0):
    row=[]
    for x in xs:
        f=top(FPb,x,y); t=top(T,x,y); w=max([top(b2,x,y) for b2 in W.values()]+[-1])
        row.append(('%.2f'%f if f==f else '  -  ')+'/'+('%.2f'%t if t==t else '-')+('/%.2f'%w if w>0 else ''))
    print('P256 y%.0f '%y,' '.join(row))
os._exit(0)

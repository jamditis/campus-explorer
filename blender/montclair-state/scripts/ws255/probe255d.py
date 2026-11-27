# ws255 read-only probe: Feliciano E base course N of y 172 vs walk/ground; ground strip x -194.7..-192
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ['F']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','WS250_W63','WS251_W63','WS253_W63','WS254_W63','WS255_W63','PI_Feliciano','Feliciano School of Business walls','Footpaths_OSM','PN_Feliciano','PO_Feliciano'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
print('P255 objs',[o.name for o in b.objects],flush=True)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,box=(-205,-180,160,200)):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'])
others={o.name:bvh(o) for o in b.objects if o.name.startswith(('WS25','Footpaths')) and o.type=='MESH'}
def top(bt,x,y):
    if bt is None: return float('nan')
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else float('nan')
xs=[-0.05,0.1,0.3,0.6,1.0,1.5,2.0,2.6]
print('P255 cols',xs)
for y in list(np.arange(179.0,183.01,0.25))+list(np.arange(189.0,197.1,0.5)):
    row=[]
    for dx in xs:
        x=-194.69+0.0615*(y-172.0)+dx
        g=top(T,x,y); s=[(n[:12],top(t,x,y)) for n,t in others.items() if top(t,x,y)==top(t,x,y)]
        best=max([g]+[v for _,v in s if v==v]) if s else g
        who='T' if (not s or best==g) else max(s,key=lambda q:q[1] if q[1]==q[1] else -1)[0][:8]
        row.append('%.2f%s'%(best,who[:6]))
    print('P255 y%.1f '%y,' '.join(row),flush=True)
os._exit(0)

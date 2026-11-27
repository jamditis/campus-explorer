# ws256 read-only probe c: who is on top (evaluated) at the junction; T = terrain pokes through
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ['F']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','WS250_W63','WS251_W63','WS253_W63d_Feliciano_E_walk','WS254_W63e_Feliciano_E_walk_N','WS255_W63f','Footpaths_OSM'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
BOX=(-197,-186,185,196)
def bvh(o):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(BOX[0]<vs[i].x<BOX[1] and BOX[2]<vs[i].y<BOX[3] for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
B={o.name:bvh(o) for o in b.objects if o.type=='MESH' and not o.name.startswith(('WS250','WS251'))}
B={k:v for k,v in B.items() if v}
def top(bt,x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else None
code={'Terrain_LiDAR_DTM_1m':'T','Footpaths_OSM':'F'}
def c(n): return code.get(n, 'P' if n.startswith('WS255') else 'E' if n.startswith('WS254') else 'W')
pokes=0
xs=np.arange(-194.0,-188.9,0.25)
print('P256C xs',xs[0],'..',xs[-1],'step .25   letter=top object, number=cm above 2nd')
for y in np.arange(187.0,192.01,0.2):
    row=[]
    for x in xs:
        hs=sorted([(top(t,x,y),n) for n,t in B.items() if top(t,x,y) is not None],reverse=True)
        if not hs: row.append(' . '); continue
        z,n=hs[0]; gap=(z-hs[1][0])*100 if len(hs)>1 else 0
        if n.startswith('Terrain') and len(hs)>1 and gap>0.3: pokes+=1
        row.append('%s%2d'%(c(n),min(99,round(gap))))
    print('P256C y%.1f '%y,' '.join(row))
print('P256C terrain-on-top-of-paving count',pokes)
os._exit(0)

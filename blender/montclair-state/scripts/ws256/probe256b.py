# ws256 read-only probe b: dense FP eval sampling at the Feliciano E junction + outlines of walk ext / W63f paving / FP base
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ['F']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','WS250_W63','WS254_W63e_Feliciano_E_walk_N','WS255_W63f','Footpaths_OSM'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
BOX=(-200,-180,186,200)
def mesh(o,ev=True):
    em=(o.evaluated_get(dg) if ev else o).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(BOX[0]<vs[i].x<BOX[1] and BOX[2]<vs[i].y<BOX[3] for i in p.vertices)]
    return vs,ps
for n in ('WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED','WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED'):
    o=bpy.data.objects[n]; vs,ps=mesh(o,False); u=sorted({i for p in ps for i in p})
    P=np.array([[vs[i].x,vs[i].y,vs[i].z] for i in u])
    print('P256B',n[:40],'n',len(u),'x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f'%(P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max(),P[:,2].min(),P[:,2].max()))
    top=P[P[:,1]>P[:,1].max()-0.3]; print('P256B   N-end verts',' '.join('(%.2f,%.2f,%.2f)'%tuple(r) for r in top[np.argsort(top[:,0])][:14]))
    print('P256B   mats',[m.name for m in o.data.materials if m], 'mods',[m.name for m in o.modifiers])
fp=bpy.data.objects['Footpaths_OSM']
vb,pb=mesh(fp,False)
print('P256B FP mats',[m.name for m in fp.data.materials if m][:6])
for p in pb:
    print('P256B FPbase poly',' '.join('(%.2f,%.2f,%.2f)'%(vb[i].x,vb[i].y,vb[i].z) for i in p))
vs,ps=mesh(fp,True)
FB=BVHTree.FromPolygons(vs,ps)
def top(bt,x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else float('nan')
# FP edge in y per x
for x in np.arange(-195,-180,0.5):
    ys=[y for y in np.arange(188,197,0.05) if top(FB,x,y)==top(FB,x,y)]
    if ys: print('P256B FPedge x%.1f y %.2f..%.2f  z@mid %.3f'%(x,min(ys),max(ys),top(FB,x,(min(ys)+max(ys))/2)))
print('P256B dense FP z, rows y, cols x -194..-185.5 step .5')
for y in np.arange(190.6,194.01,0.2):
    print('P256B y%.1f '%y,' '.join(('%.3f'%top(FB,x,y))[-5:] if top(FB,x,y)==top(FB,x,y) else '  -  ' for x in np.arange(-194,-185.4,0.5)))
os._exit(0)

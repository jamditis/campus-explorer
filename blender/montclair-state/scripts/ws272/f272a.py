# ws272a (merge208 CHAIN, on ws271c): UNIFY #4c — WS68_RHD_ground_northDTM S-edge ridge W of the Sprague grandstand lawn.
# The DTM has no returns W of x -250 here (WS68 is "dtm_filled"); its last rows (y -127...-135, x -278...-250) climb SOUTH by
# 1-2.6 m (to 122.8 at the S edge) and then drop 2-4 m to WS60_terrain_edge_apron (118.2-118.7 at y -135), with a 0.5-0.8 m pit
# at x -256...-253, y -130...-132. Real ground on both sides falls south (Terrain_LiDAR at x -248.5: 122.4 at y -126.5 ->
# 119.0 at y -135.5; WS68 W of x -270: 118.9 -> 117.7). Fix: harmonic (Laplace) fill of the fill-only cells, boundaries = row
# y -126 (kept), columns x -279 and -248.6 (kept; 1.4 m last interval weighted only at x -250), S row y -135 set onto the apron's top at the same x. Lawn only. UNVERIFIED
# (no LiDAR returns in the cells; shape = smooth fall between measured neighbours).
# Extended W to x -278: the S row stood 0.6-0.8 m above the apron there too.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F272A'; OB=bpy.data.objects
A=[o for o in OB if o.name.startswith('WS68_RHD_ground_northDTM')][0]; assert A.matrix_world.is_identity if hasattr(A.matrix_world,'is_identity') else True
ap=[o for o in OB if o.name.startswith('WS60_terrain_edge_apron')][0]; amw=ap.matrix_world
TA=BVHTree.FromPolygons([amw@v.co for v in ap.data.vertices],[p.vertices[:] for p in ap.data.polygons])
me=A.data; V=me.vertices
key={}
for v in V:
    x,y=v.co.x,v.co.y
    if abs(x-round(x))<0.01 and abs(y-round(y))<0.01 and -280<=x<=-249.5 and -136<y<-124: key[(int(round(x)),int(round(y)))]=v.index
xs=list(range(-279,-249)); ys=list(range(-126,-136,-1))
miss=[(x,y) for x in xs for y in ys if (x,y) not in key]; print(TAG,'grid verts',len(key),'missing',miss[:10],flush=True)
E_col={}
for v in V:
    if abs(v.co.x+248.6)<0.05 and -136<v.co.y<-124: E_col[int(round(v.co.y))]=v.co.z
print(TAG,'E col',sorted(E_col.items()),flush=True)
Z={k:V[i].co.z for k,i in key.items()}; Z0=dict(Z)
for x in xs:
    h=TA.ray_cast(Vector((x,-135.0+0.02,300)),Vector((0,0,-1)))
    if h[0] is None: h=TA.ray_cast(Vector((x,-135.3,300)),Vector((0,0,-1)))
    if h[0] is not None and x>-279: Z[(x,-135)]=h[0].z
def get(x,y):
    if x==-249: return E_col.get(y, Z.get((-250,y)))   # x -248.6 column, treated as the E neighbour
    return Z[(x,y)]
free=[(x,y) for x in range(-278,-249) for y in range(-127,-135,-1)]
for it in range(4000):
    mx=0
    for (x,y) in free:
        # 1 m grid except the last interval x -250 -> -248.6 (1.4 m): non-uniform second difference only there
        # (d2z/dx2 ~ 2/(h1+h2) * ((zW-z)/h1 + (zE-z)/h2)); every other vertex uses the plain 4-neighbour average.
        if x==-250: wW,wE=2/2.4,2/(2.4*1.4)
        else: wW=wE=1.0
        n=(wW*get(x-1,y)+wE*get(x+1,y)+Z[(x,y+1)]+Z[(x,y-1)])/(wW+wE+2)
        mx=max(mx,abs(n-Z[(x,y)])); Z[(x,y)]=n
    if mx<1e-4: break
print(TAG,'iters',it,'res',mx,flush=True)
d=np.array([Z[k]-Z0[k] for k in Z]); print(TAG,'changed',int((np.abs(d)>0.01).sum()),'max lower',round(d.min(),2),'max raise',round(d.max(),2),flush=True)
for y in ys:
    print(TAG,'y',y,' '.join(f'{Z[(x,y)]:.1f}' for x in range(-279,-249)),flush=True)
for k,i in key.items():
    if k in Z: V[i].co.z=Z[k]
me.update()
# objects (non-ground) whose bbox reaches into the band, for the render check
for o in OB:
    if o.type not in ('MESH','POINTCLOUD') or o is A or o is ap: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(b.x for b in bb)>-270 and min(b.x for b in bb)<-250 and max(b.y for b in bb)>-135 and min(b.y for b in bb)<-127 and (max(b.x for b in bb)-min(b.x for b in bb))<300:
        print(TAG,'near',o.name[:70],'hide_render',o.hide_render,flush=True)

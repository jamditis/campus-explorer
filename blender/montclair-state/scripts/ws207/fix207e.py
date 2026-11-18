# ws207 W29 NEW (found while probing W27): a 0.4-0.6 m wide pit between the WS79 lot patch's E edge and the WS98 raised
# walk pad's W curb (x -217.0..-216.3, y -84.8..-86.3): only LiDAR Terrain there, 17-20 cm below the lot (126.61 vs 126.81)
# and ~0.45 m below the pad top -> a dark slot at the pad foot. The 2020 ortho shows continuous lot paving up to the pad
# curb, so: one asphalt fill sheet (fn_lot_asphalt, like WS79) x -217.4..-216.0, y -84.5..-86.6, graded by inverse-distance (p3, 1.2 m) from the
# lot/aisle surfaces around it (pad excluded; a plane fit left an 8 cm ledge, rejected), tucked 3 mm under every existing lot/aisle/pad surface, running under
# the pad curb so no gap remains. Runs AFTER fix207a.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
W79=ob('WS79_lot_E_patch'); AI=ob('WS98_lotE_entry_aisle'); PAD=ob('WS98_lotE_raised_concrete_walk_pad')
LT=[bvh(W79),bvh(AI),bvh(ob('WS76_accessible_lot_asphalt')),bvh(ob('WS96_lot_E_edge_gap'))]; TP=bvh(PAD)
P=[]
for x in np.arange(-218.6,-215.4,0.1):
    for y in np.arange(-87.4,-83.6,0.1):
        if hz(TP,x,y) is not None: continue
        zz=[z for z in (hz(t,x,y) for t in LT) if z is not None]
        if zz: P.append((x,y,max(zz)))
P=np.array(P); print('F207e IDW samples',len(P),flush=True)
def idw(x,y):
    d=np.sqrt((P[:,0]-x)**2+(P[:,1]-y)**2); m=d<1.2
    if not m.any(): m=d<=d.min()+0.3
    w=1/np.maximum(d[m],0.05)**3; return float((w*P[m,2]).sum()/w.sum())
X0,X1,Y0,Y1,N=-217.4,-216.0,-86.6,-84.5,8
V=[];F=[]
for j in range(N+1):
    for i in range(N+1):
        x=X0+(X1-X0)*i/N; y=Y0+(Y1-Y0)*j/N; z=idw(x,y)-0.002
        for t in LT+[TP]:
            zo=hz(t,x,y)
            if zo is not None and z>zo-0.003: z=zo-0.003
        V.append((x,y,z))
for j in range(N):
    for i in range(N):
        a=j*(N+1)+i; F.append((a,a+1,a+N+2,a+N+1))
me=bpy.data.meshes.new('WS207_lot_pad_foot_fill'); me.from_pydata(V,[],F); me.update()
for m in W79.data.materials: me.materials.append(m)
o=bpy.data.objects.new('WS207_lot_pad_foot_fill_asphalt_ortho2020_UNVERIFIED',me)
(W79.users_collection[0] if W79.users_collection else bpy.context.scene.collection).objects.link(o)
print('F207e fill',o.name,'verts',len(V),'mat',[m.name for m in me.materials],flush=True)

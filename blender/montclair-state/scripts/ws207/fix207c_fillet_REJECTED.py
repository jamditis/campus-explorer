# ws207 W12 bite at (9,-39): wedge of bare lawn (Terrain 135.27-135.30) between the walk's E edge (135.40 @ (8.6,-38.5) ->
# 135.20 @ (9.4,-40.0)) and the dock apron's S edge (135.42 @ x 8.8 rising to 135.57 @ x 9.4). Ortho = canopy here, so the
# design call (UNVERIFIED): the walk flares into the apron as one poured concrete fillet (common where a walk meets a dock
# apron). Triangle A (walk/apron meet) - B (apron S edge) - C (walk E edge), z from the adjacent surfaces (tucked 3 mm under
# them along the shared edges, 4x subdivided), plus a vertical concrete face along the free B-C edge down to Terrain-5 cm.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
FP=ob('Footpaths_OSM'); AP=ob('CCOM_dock_apron_20261014jf3'); TER=ob('Terrain_LiDAR_DTM_1m')
fm=FP.matrix_world; vs={i for i,v in enumerate(FP.data.vertices) if 0<(fm@v.co).x<20 and -64<(fm@v.co).y<-28}
TF=BVHTree.FromPolygons([fm@v.co for v in FP.data.vertices],[tuple(p.vertices) for p in FP.data.polygons if all(i in vs for i in p.vertices)])
TA=bvh(AP); TT=bvh(TER)
def near(t,x,y,r=0.35):
    for rr in (0,0.1,0.2,r):
        zz=[hz(t,x+rr*np.cos(a),y+rr*np.sin(a)) for a in (np.linspace(0,2*np.pi,9)[:-1] if rr else [0])]; zz=[z for z in zz if z is not None]
        if zz: return float(np.mean(zz))
    return None
A=(8.62,-38.46); B=(10.0,-38.82); C=(9.42,-40.0)
zA=min(near(TF,*A),near(TA,*A))-0.003; zB=near(TA,*B)-0.003; zC=near(TF,*C)-0.003
print('F207c zA %.3f zB %.3f zC %.3f'%(zA,zB,zC),flush=True)
N=6; V=[]; F=[]; idx={}
for i in range(N+1):
    for j in range(N+1-i):
        k=N-i-j; a,b,c=i/N,j/N,k/N
        x=a*A[0]+b*B[0]+c*C[0]; y=a*A[1]+b*B[1]+c*C[1]; z=a*zA+b*zB+c*zC
        # keep tucked under walk/apron where they overlap
        for t in (TF,TA):
            zo=hz(t,x,y)
            if zo is not None and z>zo-0.003: z=zo-0.003
        idx[(i,j)]=len(V); V.append((x,y,z))
for i in range(N):
    for j in range(N-i):
        F.append((idx[(i,j)],idx[(i+1,j)],idx[(i,j+1)]))
        if j<N-i-1: F.append((idx[(i+1,j)],idx[(i+1,j+1)],idx[(i,j+1)]))
# skirt along B-C (i=0 row: j from N..0)
row=[idx[(0,j)] for j in range(N+1)]
base=[]
for r in row:
    x,y,z=V[r]; zt=hz(TT,x,y); base.append(len(V)); V.append((x,y,(zt if zt is not None else z-0.3)-0.05))
for q in range(N): F.append((row[q],row[q+1],base[q+1],base[q]))
me=bpy.data.meshes.new('WS207_CCOM_walk_apron_fillet'); me.from_pydata(V,[],F); me.update()
for p in me.polygons: p.use_smooth=False
o=bpy.data.objects.new('WS207_CCOM_walk_apron_fillet_concrete_UNVERIFIED',me)
for m in FP.data.materials: me.materials.append(m)
cols=FP.users_collection; (cols[0] if cols else bpy.context.scene.collection).objects.link(o)
print('F207c fillet verts',len(V),'faces',len(F),'mat',[m.name for m in me.materials],'col',cols[0].name if cols else 'scene',flush=True)

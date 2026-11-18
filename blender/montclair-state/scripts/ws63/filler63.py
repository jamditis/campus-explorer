# ws63: fill the pre-existing ~0.85 m2 terrain hole at x 94..99, y -56.4..-54 (seen as a black crescent beyond the walk) with a sunk draped patch
import bpy,bmesh,numpy as np,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
N='WS63_hole_filler_E'
if bpy.data.objects.get(N): print('F63 already'); raise SystemExit
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get()
m=T.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); BV=BVHTree.FromBMesh(bm)
xs=np.arange(92.5,101.01,0.25); ys=np.arange(-58,-52.49,0.25); Z=np.full((len(ys),len(xs)),np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        h=BV.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
        if h: Z[j,i]=h.z
nm=int(np.isnan(Z).sum())
while np.isnan(Z).any():
    P=np.pad(Z,1,constant_values=np.nan); nb=np.stack([P[1+a:P.shape[0]-1+a,1+b:P.shape[1]-1+b] for a in(-1,0,1) for b in(-1,0,1)])
    f=np.nanmean(np.where(np.isnan(nb),np.nan,nb),axis=0); Z=np.where(np.isnan(Z),f,Z)
Z-=0.04
me=bpy.data.meshes.new(N); nx=len(xs)
me.from_pydata([(float(x),float(y),float(Z[j,i])) for j,y in enumerate(ys) for i,x in enumerate(xs)],[],[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(ys)-1) for i in range(nx-1)])
for p in me.polygons: p.use_smooth=True
for mt in T.data.materials: me.materials.append(mt)
o=bpy.data.objects.new(N,me); T.users_collection[0].objects.link(o)
print('F63 filler built, filled',nm,'miss samples')
dg.update(); 
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('F63 saved')

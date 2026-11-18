# ws60: feather Context_skirt_3DEP_ortho_4km within BAND m outside the LiDAR terrain boundary so it meets the terrain edge height (closes the 0.5–7 m plate-edge steps on the N and W edges). Idempotent-ish (re-running converges).
import bpy,bmesh,os
from mathutils import Vector
from mathutils.kdtree import KDTree
BAND=float(os.environ.get('BAND','45'))
dg=bpy.context.evaluated_depsgraph_get()
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tb=bmesh.new(); tb.from_mesh(t.evaluated_get(dg).to_mesh()); tb.transform(t.matrix_world)
B=[(e.verts[0].co+e.verts[1].co)/2 for e in tb.edges if e.is_boundary]
kd=KDTree(len(B))
for i,p in enumerate(B): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
xs=[v.co.x for v in tb.verts]; ys=[v.co.y for v in tb.verts]; X0,X1,Y0,Y1=min(xs),max(xs),min(ys),max(ys)
s=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; mw=s.matrix_world; mi=mw.inverted()
n=0; mx=0
for v in s.data.vertices:
    w=mw@v.co
    if X0+1<w.x<X1-1 and Y0+1<w.y<Y1-1: continue   # under the terrain: leave
    co,i,d=kd.find(Vector((w.x,w.y,0)))
    if d>BAND: continue
    k=min(1.0,max(0.0,1-d/BAND)); k=k*k*(3-2*k)
    target=B[i].z-0.15   # tuck 15 cm under the terrain edge
    dz=(target-w.z)*k
    if abs(dz)>0.01: w.z+=dz; v.co=mi@w; n+=1; mx=max(mx,abs(dz))
s.data.update(); print('F60 feathered',n,'max',round(mx,2))

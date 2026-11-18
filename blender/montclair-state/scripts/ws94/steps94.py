import bpy,json,math
from mathutils.bvhtree import BVHTree
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS81_lot_seam_underlay','WS94_lot_slit')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith(pre)]
dg=bpy.context.evaluated_depsgraph_get()
T=[]
for o in d.objects:
    bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
for o in d.objects:
    me=o.evaluated_get(dg).to_mesh(); mw=o.matrix_world
    V=[mw@v.co for v in me.vertices]; F=[list(p.vertices) for p in me.polygons]
    T.append((o.name[:6],BVHTree.FromPolygons(V,F)))
x0,x1,y0,y1=-270,-212,-108,-64; st=0.1
G={}
for i in range(int((x1-x0)/st)):
    for j in range(int((y1-y0)/st)):
        x=x0+i*st; y=y0+j*st; best=None
        for n,t in T:
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if h[0] and (best is None or h[0].z>best[1]): best=(n,h[0].z)
        if best: G[(i,j)]=best
S=[]
for (i,j),(n,z) in G.items():
    for di,dj in ((1,0),(0,1)):
        q=G.get((i+di,j+dj))
        if q and abs(q[1]-z)>0.02: S.append((round(x0+i*st,1),round(y0+j*st,1),n,q[0],round(q[1]-z,3)))
print("GRID",len(G),"STEPS",len(S))
from collections import Counter
print(Counter((a[2],a[3]) for a in S).most_common(12))
print(Counter(round(a[4]/0.02)*0.02 for a in S).most_common(10))
json.dump(S,open('/workspace/nj-scenes/montclair-state/scripts/ws94/steps94.json','w'))

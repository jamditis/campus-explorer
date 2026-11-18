# ws57: local terrain cut under two pavement pokes (Roads_OSM ~(100,-10), Footpaths_OSM ~(60,-80)). Iterative: lower terrain verts above the evaluated pavement, re-evaluate drape, re-measure.
import bpy,bmesh,os,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SPOTS=[('Roads_OSM',100,-10),('Footpaths_OSM',60,-80)]
R=float(os.environ.get('RAD','4'))
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; mi=mw.inverted()
def tree(n):
    dg=bpy.context.evaluated_depsgraph_get()
    ob=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); return BVHTree.FromBMesh(bm)
def measure(n,cx,cy):
    T=tree('Terrain_LiDAR_DTM_1m'); P=tree(n); mx=0; k=0
    for x in np.arange(cx-R,cx+R,0.25):
        for y in np.arange(cy-R,cy+R,0.25):
            a=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600); b=P.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
            if a[0] and b[0] and a[0].z>b[0].z+0.01 and a[0].z-b[0].z<1.0: k+=1; mx=max(mx,a[0].z-b[0].z)
    return k,round(mx,3)
for n,cx,cy in SPOTS:
    print('L57 before',n,measure(n,cx,cy))
    for it in range(5):
        P=tree(n); moved=0
        for v in t.data.vertices:
            w=mw@v.co
            if abs(w.x-cx)>R+1 or abs(w.y-cy)>R+1: continue
            best=None
            for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5),(0.5,0.5),(-0.5,-0.5),(0.5,-0.5),(-0.5,0.5)):
                r=P.ray_cast(Vector((w.x+dx,w.y+dy,w.z+3)),Vector((0,0,-1)),6)
                if r[0]: z=r[0].z-0.06; best=z if best is None else min(best,z)
            if best is not None and w.z>best and w.z-best<1.0: w.z=best; v.co=mi@w; moved+=1
        t.data.update(); bpy.context.view_layer.update()
        m=measure(n,cx,cy); print('L57 it',it,n,'moved',moved,m)
        if m[0]==0 or moved==0: break
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('L57 saved')

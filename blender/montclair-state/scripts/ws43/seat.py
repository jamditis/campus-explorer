import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    ob=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); return BVHTree.FromBMesh(bm)
D=tree('COLE_plaza_deck_bs'); F=tree('Footpaths_OSM')
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; mi=mw.inverted(); n=0; mx=0
for v in t.data.vertices:
    w=mw@v.co; best=None
    if -215<w.x<-160 and -110<w.y<-50:
        for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
            r=D.ray_cast(Vector((w.x+dx,w.y+dy,w.z+5)),Vector((0,0,-1)),10)
            if r[0]: z=r[0].z-0.06; best=z if best is None else min(best,z)
    elif 50<w.x<66 and -86<w.y<-74:
        r=F.ray_cast(Vector((w.x,w.y,w.z+5)),Vector((0,0,-1)),10)
        if r[0]: best=r[0].z-0.04
    if best is not None and w.z>best:
        mx=max(mx,w.z-best); w.z=best; v.co=mi@w; n+=1
t.data.update(); print('S43 seated',n,'max',round(mx,2)); bpy.ops.wm.save_mainfile()

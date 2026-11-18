import bpy,bmesh,numpy as np
from mathutils import Vector
N=['Terrain_LiDAR_DTM_1m','Footpaths_OSM','Roads_OSM']
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (s,d): d.objects=[n for n in N if n in s.objects]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
src=open('/workspace/nj-scenes/montclair-state/scripts/ws57/local_seat.py').read().split('for n,cx,cy in SPOTS:')[0]
exec(src)
dg=bpy.context.evaluated_depsgraph_get()
for n,cx,cy in SPOTS:
    T=tree('Terrain_LiDAR_DTM_1m'); P=tree(n); pts=[]
    for x in np.arange(cx-R,cx+R,0.25):
        for y in np.arange(cy-R,cy+R,0.25):
            a=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600); b=P.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
            if a[0] and b[0] and a[0].z>b[0].z+0.01 and a[0].z-b[0].z<1.0: pts.append((round(x,2),round(y,2),round(a[0].z-b[0].z,2),b[3] and round(b[3],1)))
    print('D57',n,pts[:12])
    ob=bpy.data.objects[n]; me=ob.evaluated_get(dg).to_mesh(); mw=ob.matrix_world
    if pts:
        x,y=pts[0][0],pts[0][1]
        r=P.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600); fi=r[2]
        f=me.polygons[fi]; vs=[tuple(round(c,2) for c in (mw@me.vertices[i].co)) for i in f.vertices]
        print('D57 face',fi,'area',round(f.area,2),vs)
    # terrain vertex spacing
    tt=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tw=tt.matrix_world
    near=[tuple(round(c,2) for c in tw@v.co) for v in tt.data.vertices if abs((tw@v.co).x-pts[0][0])<1.2 and abs((tw@v.co).y-pts[0][1])<1.2] if pts else []
    print('D57 terrain near',near[:12])

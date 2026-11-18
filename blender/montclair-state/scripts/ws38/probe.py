import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects.get(n)
    if not o: print('missing',n); return None
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
names=['Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS27_CollegeAve_carriageway_2020ortho','Roads_OSM','WS27_CollegeAve_curb_left_UNVERIFIED','COLE_plaza_deck_bs']
T={n:bvh(n) for n in names}
def z(n,x,y):
    t=T.get(n)
    if not t: return None
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
    return r[0].z if r[0] else None
# road axis: carriageway hits along x for several y
for y in range(-140,-60,8):
    xs=[x*0.5 for x in range(-520,-300) if z('WS27_CollegeAve_carriageway_2020ortho',x*0.5,y) is not None]
    print('carr y',y, (min(xs),max(xs)) if xs else None)
for n in ['WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED']:
    o=bpy.data.objects.get(n)
    if o: 
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print(n,[round(min(p[i] for p in bb),1) for i in range(3)],[round(max(p[i] for p in bb),1) for i in range(3)])
for o in bpy.data.objects:
    if 'RedHawk' in o.name: print('obj',o.name,[round(v,2) for v in o.matrix_world.translation], round(math.degrees(o.matrix_world.to_euler().z),1))
print('GRID foot of steps: rows y, cols x -214..-199; T=terrain W=walk C=carr')
for y in range(-104,-80,2):
    row=[]
    for x in range(-214,-198,1):
        t=z('Terrain_LiDAR_DTM_1m',x,y); w=z('Footpaths_OSM',x,y); c=z('WS27_CollegeAve_carriageway_2020ortho',x,y)
        s='%5.2f'%t if t else '  -  '
        s+=('w%+.2f'%(w-t) if (w and t) else '      ')
        s+=('C' if c else ' ')
        row.append(s)
    print(y,' '.join(row))

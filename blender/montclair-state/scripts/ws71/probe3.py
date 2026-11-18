import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
B={n:bvh(n) for n in ('Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_left_UNVERIFIED','WS71_Kasser_S_sidewalk_ortho2020_UNVERIFIED_width','Alexander Kasser Theater roof (LiDAR)')}
for y in range(-54,-70,-1):
    row=[]
    for x in range(-214,-198,1):
        best=None
        for n,t in B.items():
            h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
            if h and (best is None or h.z>best[1]): best=(n[:4] if not n.startswith('WS') else n[2:6],h.z)
        row.append(f"{best[0]}{best[1]-120:.2f}" if best else '-')
    print('R71',y,' '.join(row))

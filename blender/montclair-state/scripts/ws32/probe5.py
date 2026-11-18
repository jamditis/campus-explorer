import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws32/fix.py').read())
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
D=Vector((0,0,-1))
N={'CCOM_dock_apron_20261014jf3':'A','Footpaths_OSM':'F','OZ_walk_joints_auto_GN_UNVERIFIED':'O','PA_walk_panel_tone_chips_UNVERIFIED':'P','Roads_OSM':'R','Curbs_granite_OSM':'C','Lawn_worn_edge_along_walks':'L','Terrain_LiDAR_DTM_1m':'T'}
B={}
for n,c in N.items():
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); e.to_mesh_clear()
    if len(b.faces): B[c]=BVHTree.FromBMesh(b)
    b.free()
def top(x,y):
    best=None
    for c,t in B.items():
        h=t.ray_cast(Vector((x,y,200)),D,200)
        if h[0] is not None and (best is None or h[0].z>best[1]): best=(c,h[0].z)
    return best
print('EAST')
for y in (-36,-32,-28,-24):
    print(y,' '.join(f"{x}:{top(x,y)[0]}@{top(x,y)[1]:.2f}" for x in (12,13,14,15,15.5,16,16.5,17,18,19,20,22)))
print('SEAM')
for y10 in range(-380,-230,5):
    s=''
    for x10 in range(-20,90,3):
        t=top(x10/10,y10/10); s+= t[0] if t else '.'
    print(f'{y10/10:6.1f} {s}')

import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
L=[n for n in ('Terrain_LiDAR_DTM_1m','SA_ground_lower_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','Context_skirt_3DEP_ortho_4km','Terrain') if n in bpy.data.objects]
def hit(n,x,y):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
    r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
    return round((mw@r[1]).z,2) if r[0] else None
# all-scene raycast top hit name
sc=bpy.context.scene
def top(x,y):
    r=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
    return (round(r[1].z,2), r[4].name[:40]) if r[0] else None
for y in (244,246,248.5,251,253,255.8,258,262.7,266):
    for x in (-66.0,-65,-64,-62,-60):
        print('UGT E',x,y,[hit(n,x,y) for n in L],top(x,y))
for x in (-104,-103,-102.3,-101,-100,-99):
    print('UGT W',x,250.0,[hit(n,x,250.0) for n in L],top(x,250.0))
print('UGT layers',L)

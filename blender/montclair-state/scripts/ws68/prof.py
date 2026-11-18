import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
N={'sk':'Context_skirt_3DEP_ortho_4km','ap':'WS60_terrain_edge_apron_LiDAR_to_skirt','te':'Terrain_LiDAR_DTM_1m','rd':'WS27_CollegeAve_carriageway_2020ortho','KY':'KY_college_ave_carriageway_asphalt (OSM centreli','fn':'fn_rhd_aisle_asphalt','gb':'gb_cogen_paving','ce':'ce_rhd_wall_apron','ro':'Roads_OSM','fp':'Footpaths_OSM'}
T={}
for k,v in N.items():
    n=[o.name for o in bpy.data.objects if o.name.startswith(v)][0]; T[k]=bvh(n)
def z(t,x,y):
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; return '%6.1f'%h.z if h else '   -  '
def line(lab,pts):
    print('P68',lab); print('P68      x      y  '+'  '.join('%6s'%k for k in N))
    for x,y in pts: print('P68 %6.0f %6.0f  '%(x,y)+'  '.join(z(T[k],x,y) for k in N))
line('y=-95 W-E',[(x,-95) for x in range(-330,-229,8)])
line('y=-70 W-E',[(x,-70) for x in range(-330,-229,8)])
line('y=-56 W-E',[(x,-56) for x in range(-330,-229,8)])
line('x=-262 S-N',[(-262,y) for y in range(-130,41,10)])
line('x=-240 S-N',[(-240,y) for y in range(-130,-39,10)])

import bpy, bmesh
for n in ('WS27_CollegeAve_asphalt_2020ortho','WS27_curb_concrete_UNVERIFIED'): bpy.data.materials.new(n)
def plane(name,x0,x1,y0,y1,z,s=0.5):
    bm=bmesh.new(); import numpy as np
    xs=np.arange(x0,x1+1e-6,s); ys=np.arange(y0,y1+1e-6,s); V=[[bm.verts.new((x,y,z)) for x in xs] for y in ys]
    for j in range(len(ys)-1):
        for i in range(len(xs)-1): bm.faces.new((V[j][i],V[j][i+1],V[j+1][i+1],V[j+1][i]))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); o=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(o)
plane('WS136a_Skyline_W_walk_test',-73,-68.5,-216,-202.8,126.1)
plane('WS135a_Skyline_Way_asphalt_test',-68.25,-62,-216,-195,126.0)
plane('WS142_Lot9_asphalt_test',-77,-68.25,-202.8,-195,126.3)
plane('Terrain_LiDAR_DTM_1m_test',-80,-60,-220,-190,127.0,1.0)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws145/nose145.py').read())
print('TESTOK',[(o.name[:40],len(o.data.polygons)) for o in bpy.data.objects if o.type=='MESH'])

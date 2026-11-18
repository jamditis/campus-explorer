import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import defaultdict
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
W=bvh('Alexander Kasser Theater walls'); C=bvh('WS27_CollegeAve_curb_left_UNVERIFIED'); T=bvh('Terrain_LiDAR_DTM_1m')
# march from road (y low) north along +y at each x, at z = terrain+1
for x in range(-248,-200,3):
    cy=None; wy=None
    for i in range(0,250):
        y=-75+i*0.1
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if not h: continue
        c=C.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if c: cy=y
    if cy:
        cz=C.ray_cast(Vector((x,cy,300)),Vector((0,0,-1)))[0].z
        hw=W.ray_cast(Vector((x,cy,cz+1.5)),Vector((0,1,0)),40)[0]
        if hw: wy=hw.y
    prof=[]
    if cy and wy:
        for k in range(6):
            y=cy+(wy-cy)*k/5; h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; prof.append(round(h.z,2) if h else None)
    c2=C.ray_cast(Vector((x,cy,300)),Vector((0,0,-1)))[0] if cy else None
    print('Q71',x,'curbNmax',cy and round(cy,1),'curbtop',c2 and round(c2.z,2),'wall',wy and round(wy,1),'terr',prof)

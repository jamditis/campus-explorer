import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,ev=False):
    e=o.evaluated_get(dg) if ev else o; m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'],True); K=bvh(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],True); S=bvh(bpy.data.objects['eu_rhd_ground_slab'])
for nm,B in (('terrain',T),('skirt',K)):
    bad=0;n=0;mx=0;where=[]
    for y in range(-43,27,1):
        for x in range(-256,-238,1):
            s=S.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; p=B.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
            if s and p:
                n+=1
                if p.z>s.z-0.02: bad+=1; mx=max(mx,p.z-s.z); where.append((x,y))
    print('CM68',nm,'in slab',n,'above',bad,'max',round(mx,2),'x',min([w[0] for w in where],default=0),max([w[0] for w in where],default=0),'y',min([w[1] for w in where],default=0),max([w[1] for w in where],default=0))

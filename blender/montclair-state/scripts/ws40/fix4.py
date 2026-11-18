import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    o=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(o.evaluated_get(dg).to_mesh()); bm.transform(o.matrix_world); return BVHTree.FromBMesh(bm)
SW=tree('WS40_CollegeAve_east_sidewalk_to_Kasser_steps_concrete_OSM_JOE'); CL=tree('WS27_CollegeAve_curb_left_UNVERIFIED')
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; mi=mw.inverted(); n=0
for v in t.data.vertices:
    w=mw@v.co
    if not (-199<w.x<-188 and -107<w.y<-81): continue
    best=None
    for T,off in ((SW,0.08),(CL,0.10)):
        for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
            r=T.ray_cast(Vector((w.x+dx,w.y+dy,w.z+5)),Vector((0,0,-1)),20)
            if r[0]:
                z=r[0].z-off; best=z if best is None else min(best,z)
    if best is not None and w.z>best:
        w.z=best; v.co=mi@w; n+=1
t.data.update(); print('F4 terrain lowered',n)
bpy.ops.wm.save_mainfile()

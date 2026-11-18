import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
SAVE=os.environ.get('SAVE')=='1'
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_'))]
def gz(x,y):
    z=[h[0].z for b in G for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]
    return max(z) if z else 136.
SPEC={
 'WA2_CAM_oblique_richardson_west_walks_from_SW':[(40,285,'+20'),(63,308,'+0'),30],
 'WA2_CAM_eye_richardson_west_walk_from_W':[(45,313,'+1.7'),(66,306,'+0.3'),30],
 'WA2_CAM_eye_richardson_west_walk_from_N':[(62,326,'+1.7'),(64,305,'+0.3'),30],
 'WA2_CAM_closeup_richardson_west_walk_edge':[(57.5,306,'+0.9'),(61.5,310,'+0.0'),35],
}
col=O['WA0_richardson_wall_foot_fill_UNVERIFIED'].users_collection[0]
for n,(p,t,l) in SPEC.items():
    P=Vector((p[0],p[1],gz(p[0],p[1])+float(p[2]))); T=Vector((t[0],t[1],gz(t[0],t[1])+float(t[2])))
    cam=O.get(n)
    if not cam:
        cam=bpy.data.objects.new(n,bpy.data.cameras.new(n)); col.objects.link(cam)
    cam.location=P; cam.data.lens=l; cam.data.clip_start=.1; cam.data.clip_end=5000
    cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler()
    print('CAM',n,[round(c,2) for c in P])
if SAVE: bpy.ops.wm.save_mainfile(compress=True); print('SAVED')

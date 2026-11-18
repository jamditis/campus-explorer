# ws133d: ground (evaluated GN terrain/fills) covered parts of the WS133 E walk in the eye view: lift walk top verts to
# >= evaluated ground + 3 cm and the bed to >= ground + 1 cm (skirts follow their top vert).
import bpy, os
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
w=bpy.data.objects['WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints']; b=bpy.data.objects['WS133_Russ_E_wall_foot_bed_mulch_LiDAR2023lowint_UNVERIFIED']
GROUND=('Terrain_LiDAR','WS113_terrain','WS114_terrain','WS133b_','WS60_terrain','Context_skirt','WS110_ground')
for o in (w,b): o.hide_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
def ground(x,y):
    z=300.0
    for _ in range(8):
        r=sc.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)))
        if not r[0]: return None
        if r[4].name.startswith(GROUND): return r[1].z
        z=r[1].z-0.005
    return None
for o,off in ((w,0.03),(b,0.01)):
    me=o.data; mw=o.matrix_world; n=0; mx=0
    # pair skirt verts with top verts by xy
    byxy={}
    for v in me.vertices: byxy.setdefault((round(v.co.x,3),round(v.co.y,3)),[]).append(v)
    for key,vs in byxy.items():
        top=max(vs,key=lambda v:v.co.z); p=mw@top.co; g=ground(p.x,p.y)
        if g is None: continue
        d=g+off-p.z
        if d>0:
            for v in vs: v.co.z+=d
            n+=1; mx=max(mx,d)
    me.update(); print('LIFT',o.name[:40],n,'max %.3f'%mx)
for o in (w,b): o.hide_viewport=False
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

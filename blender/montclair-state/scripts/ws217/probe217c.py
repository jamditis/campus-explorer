import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
@bpy.app.handlers.persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
print('MATS',[m.name for m in bpy.data.materials if 'rick' in m.name])
SL=next(o for o in bpy.data.objects if o.name.startswith('WS215_RHD'))
M=SL.matrix_world; P=[p for p in SL.data.polygons if (M.to_3x3()@p.normal).z>0.7]
T=BVHTree.FromPolygons([M@v.co for v in SL.data.vertices],[p.vertices[:] for p in P])
for nm in ('LH_rhd_se_wall_foot_dirt','LI_rhd_se_wall_foot_gap_fill','LJ_rhd_se_rising_damp','LH_rhd_se_door_scuff','bx2_rhd_se_core_foot_reveal'):
    o=next(o for o in bpy.data.objects if o.name.startswith(nm)); Mo=o.matrix_world
    zs=[];dd=[]
    for v in o.data.vertices:
        w=Mo@v.co; h=T.ray_cast(Vector((w.x,w.y,200)),Vector((0,0,-1)),300)
        if h[0] is not None: dd.append(round(w.z-h[0].z,3))
    print('OBJ',nm,o.hide_render,o.data.materials[0].name if o.data.materials else None,'n',len(o.data.vertices),'overwalk',len(dd),'dz min/max',min(dd) if dd else None,max(dd) if dd else None, 'zrange',round(min((Mo@v.co).z for v in o.data.vertices),2),round(max((Mo@v.co).z for v in o.data.vertices),2),flush=True)

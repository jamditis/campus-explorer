import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws81/terrain81.py').read())
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
oe=T.evaluated_get(dg); m=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(T.matrix_world); TB=BVHTree.FromBMesh(b); b.free(); oe.to_mesh_clear()
def hz(x,y):
    h=TB.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; return h.z if h else None
for y in (-120,-124,-128,-130,-132,-134,-136,-138):
    print('WS81C row',y,' '.join('%.2f'%(hz(x,y) or 0) for x in range(-248,-226,3)),flush=True)
for o in bpy.data.objects:
    if not o.name.startswith('T_') or o.type!='MESH': continue
    x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
    if not (-256<x<-229 and -140<y<-119): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; minz=min(p.z for p in bb); g=hz(x,y)
    if g is not None and minz>g-0.15:
        sh=minz-(g-0.25); o.location.z-=sh; print('WS81C tree reseat',o.name,round(sh,2),flush=True)
bpy.ops.wm.save_mainfile(); print('WS81C SAVED',flush=True)

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import os; os.chdir('/workspace/nj-scenes/montclair-state')
dg=bpy.context.evaluated_depsgraph_get()
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
Pe=P.evaluated_get(dg); pme=Pe.to_mesh()
bp=BVHTree.FromPolygons([P.matrix_world@v.co for v in pme.vertices],[tuple(p.vertices) for p in pme.polygons]); Pe.to_mesh_clear()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
bs=BVHTree.FromPolygons([sk.matrix_world@v.co for v in sme.vertices],[tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()
def gz(x,y):
    h=bp.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    if h[0] is not None: return h[0].z
    h=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return h[0].z if h[0] is not None else None
def setcam(name,loc,look,lens=32):
    o=bpy.data.objects.get(name)
    if o is None:
        c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=Vector(loc); o.rotation_euler=(Vector(look)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens; o.data.clip_end=30000; o['wf_obj']=1
    print(name,[round(v,2) for v in loc],'g',gz(loc[0],loc[1]))
# tree 004 @ 246.5,321.5 — cam west on patch
tx,ty=246.5,321.5; tg=gz(tx,ty)
for cx,cy in [(238,324),(240,328),(252,328),(246.5,330),(235,321.5)]:
    cg=gz(cx,cy); print('try',cx,cy,cg)
cx,cy=238.0,324.0; cg=gz(cx,cy)
setcam('WF_CAM_closeup_tree_bases_east_slope', (cx,cy,cg+1.7), (tx,ty,tg+0.25), 40)
bpy.ops.wm.save_mainfile(); print('SAVED')

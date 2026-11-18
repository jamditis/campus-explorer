import bpy,os,sys
from mathutils import Vector
CN='PK_cams_20261101pk'
def cam(name,loc,tgt,lens):
    if name in bpy.data.objects:
        o=bpy.data.objects[name]; d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
    if os.environ.get('REVERT')=='1': return
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_end=3000
    o=bpy.data.objects.new(name,c); o.location=loc
    o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    col=bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
    if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
    col.objects.link(o)
cam('PK_CAM_closeup_feliciano_west_base',(-268.0,188.0,135.6),(-257.6,199.0,134.0),30)
F=bpy.data.objects.get('PK_Feliciano_west_DTM_fill_UNVERIFIED')
def gz(x,y):
    if F is None: return 134.0
    from mathutils.bvhtree import BVHTree
    global _bt
    try: _bt
    except NameError:
        _bt=BVHTree.FromPolygons([F.matrix_world@v.co for v in F.data.vertices],[list(p.vertices) for p in F.data.polygons])
    h=_bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else 134.0
cam('PK_CAM_eye_feliciano_NW',(-282.0,251.0,gz(-282.0,251.0)+1.7),(-252.0,222.0,gz(-282.0,251.0)+5.0),26)
cam('PK_CAM_oblique_feliciano_from_NW',(-330.0,275.0,195.0),(-228.0,190.0,138.0),35)
if os.environ.get('REVERT')=='1' and CN in bpy.data.collections: bpy.data.collections.remove(bpy.data.collections[CN])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PKC_DONE',len(bpy.data.objects))

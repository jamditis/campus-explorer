import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import os; os.chdir('/workspace/nj-scenes/montclair-state')
# Rebuild local tree BVH around east slope trees
C=Vector((250,400,120))
TV=[];TF=[];off=0
for o in bpy.data.objects:
    if o.name.startswith('TL_tree') and (o.matrix_world.translation.xy-C.xy).length<50:
        for v in o.data.vertices: TV.append(o.matrix_world@v.co)
        for f in o.data.polygons: TF.append([i+off for i in f.vertices])
        off=len(TV)
TB=BVHTree.FromPolygons(TV,TF)
def clear(a,b):
    d=b-a; L=d.length
    if L<1e-3: return True
    return TB.ray_cast(a,d.normalized(),L)[0] is None
# target: tree base area on escarpment ~ (250,400,115)
tgt=Vector((248,398,114))
best=None
for rad in [6,8,10,12,15]:
    for a in range(0,360,15):
        for z in (116,118,120,122,125):
            p=Vector((248+rad*math.cos(math.radians(a)), 398+rad*math.sin(math.radians(a)), z))
            if clear(p,tgt) and clear(p,tgt+Vector((0,0,2))):
                best=(p,tgt); break
        if best: break
    if best: break
print('tree close',best)
def setcam(name,loc,look,lens=28):
    o=bpy.data.objects.get(name)
    if o is None:
        c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=loc; o.rotation_euler=(look-loc).to_track_quat('-Z','Y').to_euler(); o.data.lens=lens; o['wf_obj']=1
if best:
    setcam('WF_CAM_closeup_tree_bases_east_slope', best[0], best[1], 28)
# N stair closeup from NW elevated (clear)
C2=Vector((225,414,133)); TV=[];TF=[];off=0
for o in bpy.data.objects:
    if o.name.startswith('TL_tree') and (o.matrix_world.translation.xy-C2.xy).length<35:
        for v in o.data.vertices: TV.append(o.matrix_world@v.co)
        for f in o.data.polygons: TF.append([i+off for i in f.vertices])
        off=len(TV)
TB=BVHTree.FromPolygons(TV,TF)
tgt=Vector((226,413.5,133.0)); best=None
for rad in [5,7,9,11]:
    for a in range(90,200,10):  # prefer NW-N
        for z in (135,137,139,141):
            p=Vector((226+rad*math.cos(math.radians(a)), 413.5+rad*math.sin(math.radians(a)), z))
            if clear(p,tgt):
                best=(p,tgt); break
        if best: break
    if best: break
print('stair close',best)
if best:
    setcam('WF_CAM_closeup_patch_ground_N_stair', best[0], best[1], 28)
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))

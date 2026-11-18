import bpy, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import os; os.chdir('/workspace/nj-scenes/montclair-state')
# Ensure cams: reuse TI oblique; add eye NW, eye SE/east slope, closeup tree bases or patch edge / N stair
existing=[n for n in bpy.data.objects.keys() if 'CAM' in n and any(s in n for s in ('TI_','WE_','WD_','TJ_','WF_','Bohn','east_dorm','Blanton'))]
print('cands',sorted(existing)[:40])

def ensure_cam(name, loc, look, lens=35):
    o=bpy.data.objects.get(name)
    if o is None:
        cam=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,cam)
        bpy.context.scene.collection.objects.link(o)
    o.location=loc; o['wf_obj']=1
    # aim
    direction=look-loc; rot=direction.to_track_quat('-Z','Y')
    o.rotation_euler=rot.to_euler(); o.data.lens=lens
    return o

# Build tree BVH near Bohn N for clear cams (like we)
C=Vector((224.7,414.2,133.3))
TV=[]; TF=[]; off=0
for o in bpy.data.objects:
    if o.name.startswith('TL_tree') and (o.matrix_world.translation.xy-C.xy).length<40:
        for v in o.data.vertices: TV.append(o.matrix_world@v.co)
        for f in o.data.polygons: TF.append([i+off for i in f.vertices])
        off=len(TV)
TB=BVHTree.FromPolygons(TV,TF) if TV else None

def clear_ray(a,b):
    if TB is None: return True
    d=(b-a); L=d.length
    if L<1e-3: return True
    h=TB.ray_cast(a, d.normalized(), L)
    return h[0] is None

# Eye from NW looking at east dorms / patch (elevated)
eye1=Vector((160,480,145)); look1=Vector((220,400,130))
# Eye from SE looking up the escarpment / tree bases on new ground
eye2=Vector((290,360,125)); look2=Vector((220,400,130))
# Closeup: tree bases on patch east of Bohn (escarpment) OR N stair on new ground
# Prefer N stair from WE clear position elevated
close=Vector((218,420,136)); lookc=Vector((226,413,133))

# search clear closeup near stair
best=None
for rad in [2,4,6,8,10]:
    for a in range(0,360,20):
        for z in (134,136,138,140):
            p=Vector((226+rad*math.cos(math.radians(a)), 413+rad*math.sin(math.radians(a)), z))
            tgt=Vector((226,413,133.2))
            if clear_ray(p,tgt) and clear_ray(p,tgt+Vector((0,0,1))):
                best=(p,tgt); break
        if best: break
    if best: break
if best:
    close,lookc=best
    print('closeup clear', [round(x,2) for x in close], '->', [round(x,2) for x in lookc])
else:
    print('closeup fallback (may be occluded)')

ensure_cam('WF_CAM_eye_east_dorms_from_NW', eye1, look1, 32)
ensure_cam('WF_CAM_eye_east_slope_from_SE', eye2, look2, 32)
ensure_cam('WF_CAM_closeup_patch_ground_N_stair', close, lookc, 28)
# also a tree-base closeup on escarpment
ensure_cam('WF_CAM_closeup_tree_bases_east_slope', Vector((255,395,118)), Vector((250,400,115)), 28)

# verify TI exists
print('TI', bpy.data.objects.get('TI_CAM_oblique_east_dorms_from_SW') is not None)
print('WE', bpy.data.objects.get('WE_CAM_eye_Bohn_N_stair_clear') is not None)
bpy.ops.wm.save_mainfile()
print('SAVED cams', len(bpy.data.objects))
json.dump(dict(close=[list(close),list(lookc)]), open('data/wf/cams.json','w'))

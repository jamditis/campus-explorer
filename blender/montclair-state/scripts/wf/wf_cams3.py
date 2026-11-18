# Fix WF cams: place above new ground, clear of trees, looking at useful targets
import bpy, math, json
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

# tree BVH whole east dorm box (coarse: trunks+crowns)
TV=[];TF=[];off=0
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree'): continue
    p=o.matrix_world.translation
    if not (50<=p.x<=300 and 320<=p.y<=520): continue
    for v in o.data.vertices: TV.append(o.matrix_world@v.co)
    for f in o.data.polygons: TF.append([i+off for i in f.vertices])
    off=len(TV)
TB=BVHTree.FromPolygons(TV,TF)
def clear(a,b):
    d=b-a; L=d.length
    if L<1e-3: return True
    return TB.ray_cast(a, d.normalized(), L)[0] is None

def setcam(name,loc,look,lens=32):
    o=bpy.data.objects.get(name)
    if o is None:
        c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=Vector(loc); o.rotation_euler=(Vector(look)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens; o.data.clip_end=30000; o['wf_obj']=1
    print('CAM',name,[round(x,2) for x in loc],'->',[round(x,2) for x in look],'g',gz(loc[0],loc[1]))

# Eye NW: west of Bohn looking SE at dorms + patch
# Try positions on open lawn west of Bohn
look=Vector((230,400,138))
best=None
for x in range(140,190,5):
    for y in range(430,490,5):
        g=gz(x,y)
        if g is None: continue
        for h in (1.6, 2.0, 3.0, 5.0, 8.0, 12.0):
            p=Vector((x,y,g+h))
            if clear(p, look) and clear(p, look+Vector((0,0,-5))):
                best=(p,look,h); break
        if best and best[2]<=3.0: break
    if best and best[2]<=3.0: break
print('NW search',best)
if best: setcam('WF_CAM_eye_east_dorms_from_NW', best[0], best[1], 32)
else:
    g=gz(155,460) or 136
    setcam('WF_CAM_eye_east_dorms_from_NW', (155,460,g+8), (230,400,136), 32)

# Eye from W looking at Bohn W face + walks on new ground (reuse area of WD eye but higher)
look2=Vector((220,405,136))
best=None
for x in range(175,205,3):
    for y in range(390,430,4):
        g=gz(x,y)
        if g is None: continue
        for h in (1.7, 2.2, 3.5, 5.0):
            p=Vector((x,y,g+h))
            if (p.xy-look2.xy).length<8: continue
            if clear(p, look2):
                best=(p,look2,h); break
        if best and best[2]<=2.5: break
    if best and best[2]<=2.5: break
print('W eye search',best)
if best: setcam('WF_CAM_eye_east_slope_from_SE', best[0], best[1], 35)  # reuse name as second eye (W side)
else:
    g=gz(190,400) or 135
    setcam('WF_CAM_eye_east_slope_from_SE', (190,400,g+3), (220,405,136), 35)

# Closeup: tree base on patch — find a TL_tree with clear view of its trunk base
cands=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree'): continue
    p=o.matrix_world.translation
    if not (200<=p.x<=270 and 360<=p.y<=450): continue
    g=gz(p.x,p.y)
    if g is None: continue
    cands.append((o.name,p,g))
print('tree cands',len(cands))
best=None
for nm,p,g in cands[::3]:
    tgt=Vector((p.x,p.y,g+0.3))
    for rad in (3.0,4.0,5.0,6.0):
        for a in range(0,360,20):
            cam=Vector((p.x+rad*math.cos(math.radians(a)), p.y+rad*math.sin(math.radians(a)), g+1.4))
            # don't go through ground
            cg=gz(cam.x,cam.y)
            if cg is None or cam.z < cg+0.8: continue
            if clear(cam, tgt):
                best=(cam,tgt,nm); break
        if best: break
    if best: break
print('tree closeup',best)
if best:
    setcam('WF_CAM_closeup_tree_bases_east_slope', best[0], best[1], 28)
else:
    # patch edge closeup near Bohn W walk
    g=gz(210,405) or 135
    setcam('WF_CAM_closeup_tree_bases_east_slope', (205,408,g+1.5), (215,405,g+0.2), 28)

# Extra: N stair closeup from clear WE-like position but verify ground
look3=Vector((226,413.5,133.5))
best=None
for a in range(100,220,10):
    for rad in (6,8,10,12):
        for h in (2.0,3.0,4.0,6.0):
            x=226+rad*math.cos(math.radians(a)); y=413.5+rad*math.sin(math.radians(a))
            g=gz(x,y)
            if g is None: continue
            p=Vector((x,y,g+h))
            if clear(p, look3):
                best=(p,look3); break
        if best: break
    if best: break
print('stair close',best)
if best:
    setcam('WF_CAM_closeup_patch_ground_N_stair', best[0], best[1], 28)

bpy.ops.wm.save_mainfile()
print('SAVED',len(bpy.data.objects))
json.dump({'ok':True}, open('data/wf/cams3.json','w'))

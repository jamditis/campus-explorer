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
    if h[0] is not None: return h[0].z,'patch'
    h=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return (h[0].z,'skirt') if h[0] is not None else (None,None)

# building exclusion rough boxes from OSM
BBOX=[(200.7,249.4,344.3,414.8),(70.3,135.2,281.2,333.7),(81.9,147.4,351.4,388.3),(88.6,194.7,413.7,487.2)]
def in_bldg(x,y):
    for x0,x1,y0,y1 in BBOX:
        if x0-2<=x<=x1+2 and y0-2<=y<=y1+2: return True
    return False

# verify a few trees
SINK=-0.25
rows=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree'): continue
    p=o.matrix_world.translation
    if not (50<=p.x<300 and 320<=p.y<520): continue
    mw=o.matrix_world
    bases=[(mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p.xy).length<0.3]
    tb=min(bases) if bases else p.z
    g,src=gz(p.x,p.y)
    if g is None: continue
    err=(g+SINK)-tb
    rows.append((abs(err),o.name,p.x,p.y,tb,g,src,err,o.get('wf_dz')))
rows.sort()
print('best seated',rows[:5])
print('worst',rows[-5:])

# pick a well-seated tree on patch for closeup (prefer east slope x>230)
good=[r for r in rows if r[6]=='patch' and abs(r[7])<0.05 and r[2]>230]
print('good east',len(good), good[:3] if good else None)
# tree BVH local
def make_tb(cx,cy,r=40):
    TV=[];TF=[];off=0
    for o in bpy.data.objects:
        if not o.name.startswith('TL_tree'): continue
        p=o.matrix_world.translation
        if (p.x-cx)**2+(p.y-cy)**2 > r*r: continue
        for v in o.data.vertices: TV.append(o.matrix_world@v.co)
        for f in o.data.polygons: TF.append([i+off for i in f.vertices])
        off=len(TV)
    return BVHTree.FromPolygons(TV,TF) if TV else None
def clear(TB,a,b):
    if TB is None: return True
    d=b-a; L=d.length
    if L<1e-3: return True
    return TB.ray_cast(a,d.normalized(),L)[0] is None

def setcam(name,loc,look,lens=32):
    o=bpy.data.objects.get(name)
    if o is None:
        c=bpy.data.cameras.new(name); o=bpy.data.objects.new(name,c); bpy.context.scene.collection.objects.link(o)
    o.location=Vector(loc); o.rotation_euler=(Vector(look)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens; o.data.clip_end=30000; o['wf_obj']=1
    g,s=gz(loc[0],loc[1])
    print('CAM',name,[round(x,2) for x in loc],'g',round(g,2) if g else None,s,'in_bldg',in_bldg(loc[0],loc[1]))

# Eye NW: OUTSIDE buildings — north of Blanton / west of Bohn open lawn
# try x 50-85 (west of Blanton) or x 195-210 between Blanton and Bohn, y 490-510 north
look=Vector((220,420,140))
best=None
for x in list(range(50,85,5))+list(range(195,210,3))+list(range(250,290,5)):
    for y in list(range(490,520,5))+list(range(300,340,5))+list(range(450,485,5)):
        if in_bldg(x,y): continue
        g,s=gz(x,y)
        if g is None or s!='patch': continue
        for h in (2.0,3.5,6.0,10.0,15.0):
            p=Vector((x,y,g+h))
            TB=make_tb(x,y,35)
            if clear(TB,p,look):
                best=(p,look,h,x,y); break
        if best and best[2]<=6: break
    if best and best[2]<=6: break
print('NW',best)
if best: setcam('WF_CAM_eye_east_dorms_from_NW', best[0], best[1], 28)
else:
    # elevated from NE open slope
    g,_=gz(280,480); g=g or 115
    setcam('WF_CAM_eye_east_dorms_from_NW', (280,480,g+25), (220,400,135), 28)

# Second eye: from SW open lawn looking at Bohn/Blanton (Webster lawn is OK to stand on)
look2=Vector((210,400,138))
best=None
for x in range(90,160,5):
    for y in range(330,370,5):
        if in_bldg(x,y): continue
        g,s=gz(x,y)
        if g is None: continue
        for h in (1.7,2.5,4.0,8.0):
            p=Vector((x,y,g+h))
            TB=make_tb(x,y,30)
            if clear(TB,p,look2):
                best=(p,look2,h); break
        if best and best[2]<=3: break
    if best and best[2]<=3: break
print('SW eye',best)
if best: setcam('WF_CAM_eye_east_slope_from_SE', best[0], best[1], 32)
else:
    g,_=gz(120,340); g=g or 136
    setcam('WF_CAM_eye_east_slope_from_SE', (120,340,g+4), (210,400,138), 32)

# Closeup: well-seated tree, cam 4-6m out, 1.5m up, verify not in ground
if good:
    nm,x,y,tb,g,src,err,wdz = good[0][1],good[0][2],good[0][3],good[0][4],good[0][5],good[0][6],good[0][7],good[0][8]
    tgt=Vector((x,y,g+0.15))
    TB=make_tb(x,y,25)
    best=None
    for rad in (4.0,5.0,6.0,7.0,8.0):
        for a in range(0,360,15):
            cx=x+rad*math.cos(math.radians(a)); cy=y+rad*math.sin(math.radians(a))
            if in_bldg(cx,cy): continue
            cg,cs=gz(cx,cy)
            if cg is None: continue
            p=Vector((cx,cy,cg+1.55))
            if clear(TB,p,tgt) and clear(TB,p,tgt+Vector((0,0,1.5))):
                best=(p,tgt,nm); break
        if best: break
    print('tree close',best, 'tree',nm,'err',err)
    if best: setcam('WF_CAM_closeup_tree_bases_east_slope', best[0], best[1], 35)

# Patch-edge closeup as alternate detail: where patch meets skirt on open lawn south of Bohn
# sample edge near (200,330)
g,_=gz(200,325); g=g or 136
setcam('WF_CAM_closeup_patch_ground_N_stair', (195,318,g+2.0), (205,340,g+0.2), 28)  # reuse name for patch edge south

bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))

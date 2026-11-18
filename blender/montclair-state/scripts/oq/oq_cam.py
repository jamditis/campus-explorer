import bpy, bmesh, os, sys, math, ast
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE='--save' in sys.argv; REV=os.environ.get('REVERT')=='1'
COL='OQ_skirt_window_cams_20261031oq'
c=bpy.data.collections.get(COL)
if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile()
    raise SystemExit
c=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(c)
dg=bpy.context.evaluated_depsgraph_get(); scn=bpy.context.scene
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=ter.evaluated_get(dg); b=bmesh.new(); b.from_mesh(te.to_mesh()); b.transform(ter.matrix_world); tt=BVHTree.FromBMesh(b)
def tz(x,y):
    h=tt.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
W=[ast.literal_eval(l) for l in open('data/oq/skirt_windows.txt') if l.strip()]
def cam(name,target,frm,lens=28):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=3000
    o=bpy.data.objects.new(name,cd); c.objects.link(o); o.location=frm
    o.rotation_euler=(target-frm).to_track_quat('-Z','Y').to_euler(); print('CAM',name,tuple(round(x,1) for x in frm),'->',tuple(round(x,1) for x in target))
def pickcam(pref,dist,hgt,lens,name,ox=0):
    best=None
    for w in W:
        if not w[0].startswith(pref): continue
        o=Vector((w[1],w[2],w[3]+0.9)); n=Vector((w[4],w[5],0))
        side=Vector((-n.y,n.x,0))*ox
        q=o+n*dist+side; g=tz(q.x,q.y)
        if g is None: continue
        hh=scn.ray_cast(dg,Vector((q.x,q.y,g+60)),Vector((0,0,-1)),distance=80)
        if not hh[0] or hh[1].z>g+1.0 or hh[1].z<g-0.5: continue
        frm=Vector((q.x,q.y,hh[1].z+hgt))
        if scn.ray_cast(dg,frm,Vector((0,0,1)),distance=40)[0]: continue
        d=(o-frm); hit=scn.ray_cast(dg,frm,d.normalized(),distance=d.length-0.3)[0]
        if hit: continue
        # count windows visible in a cone
        score=sum(1 for v in W if (Vector((v[1],v[2],0))-Vector((w[1],w[2],0))).length<12)
        if best is None or score>best[0]: best=(score,frm,o)
    if best: cam(name,best[2],best[1],lens)
    else: print('NOCAM',name)
pickcam('Center for C',7.0,1.7,30,'OQ_CAM_closeup_CCIS_skirt_windows',ox=2.5)
pickcam('Calcia Hall',22.0,1.7,28,'OQ_CAM_eye_calcia_skirt_windows',ox=6)
if not bpy.data.objects.get('OQ_CAM_eye_calcia_skirt_windows'): pickcam('Speech Buil',20.0,1.7,28,'OQ_CAM_eye_speech_skirt_windows',ox=5)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

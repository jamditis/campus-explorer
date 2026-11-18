import bpy, bmesh, os, sys, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE='--save' in sys.argv; REV=os.environ.get('REVERT')=='1'
COL='OP_road_cams_20261031op'
c=bpy.data.collections.get(COL)
if c:
    for o in list(c.objects): bpy.data.objects.remove(o)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED');
    if SAVE: bpy.ops.wm.save_mainfile()
    raise SystemExit
c=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(c)
dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; te=ter.evaluated_get(dg); b=bmesh.new(); b.from_mesh(te.to_mesh()); b.transform(ter.matrix_world); tt=BVHTree.FromBMesh(b)
def tz(x,y):
    h=tt.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
rd=bpy.data.objects['Roads_OSM']; mw=rd.matrix_world
def pick(xr,yr):
    best=None
    for v in rd.data.vertices:
        p=mw@v.co
        if not(xr[0]<p.x<xr[1] and yr[0]<p.y<yr[1]): continue
        t=tz(p.x,p.y)
        if t is None: continue
        f=p.z-t
        if best is None or f<best[0]: best=(f,p.copy(),t)
    return best
def cam(name,target,frm,lens=28):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=3000
    o=bpy.data.objects.new(name,cd); c.objects.link(o); o.location=frm
    d=(target-frm); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); print('CAM',name,tuple(round(x,1) for x in frm),'->',tuple(round(x,1) for x in target))
for nm,xr,yr,dist in (('OP_CAM_closeup_redraped_road_E_of_schmitt',(150,200),(100,150),16),('OP_CAM_eye_redraped_road_E_campus_edge',(100,150),(10,50),30)):
    bp=pick(xr,yr); print(nm,'float',round(bp[0],2),tuple(round(x,1) for x in bp[1]))
    p=bp[1]; t=Vector((p.x,p.y,bp[2]+0.4))
    best=None
    for a in range(0,360,30):
        q=Vector((p.x+dist*math.cos(math.radians(a)),p.y+dist*math.sin(math.radians(a))))
        z=tz(q.x,q.y)
        if z is None: continue
        frm=Vector((q.x,q.y,z+1.7))
        hit,loc,_,_,ob,_=bpy.context.scene.ray_cast(dg,frm,(t-frm).normalized(),distance=(t-frm).length-0.5) if False else (False,None,None,None,None,None)
        best=frm; break
    cam(nm,t,best)
cam('OP_CAM_oblique_redraped_roads_E_campus',Vector((160,80,tz(160,80) or 110)),Vector((290,-40,(tz(160,80) or 110)+110)),35)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

# ws106: thin white curb-back reveal along the W curb (WS27 curb_right, o+=W) N of the College Ave table, s -6.5..-1.0.
# The 1 m terrain grid sags between verts so the curb's vertical back shows as a white strip. Additive lawn backfill strip:
# from the curb back (top - 1 cm) feathering into the terrain 0.7 m behind (1 cm under it). Only where a reveal > 2 cm exists.
import bpy,bmesh,numpy as np,sys,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws104'); from frame104 import *
O=bpy.data.objects
for o in [o for o in O if o.name.startswith('WS106_')]: O.remove(o)
def getW(ob):
    me=ob.data; n=len(me.vertices); c=np.empty(n*3); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world); return c@M[:3,:3].T+M[:3,3]
cb=[o for o in O if o.name.startswith('WS27_CollegeAve_curb_right')][0]; CW=getW(cb)
box=(CW[:,0]>-245)&(CW[:,0]<-190)&(CW[:,1]>-185)&(CW[:,1]<-135); CW=CW[box]
SO=np.array([so(q) for q in CW])
T=O['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get(); Te=T.evaluated_get(dg)
me=Te.to_mesh(); M=T.matrix_world
bvh=BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); Te.to_mesh_clear()
def tz(x,y):
    h=bvh.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),500); return h[0].z if h[0] else None
rows=[]; log=[]
for s in np.round(np.arange(-6.5,-0.99,0.25),3):
    m=(np.abs(SO[:,0]-s)<0.2)&(SO[:,1]>2.8)
    if m.sum()<2: continue
    ob=SO[m,1].max(); mt=m&(SO[:,1]>ob-0.06); top=float(CW[mt,2].max())
    p,n=frame(s); pts=[]
    for oo in (ob-0.02,ob+0.2,ob+0.45,ob+0.7):
        q=p+n*oo; pts.append((float(q[0]),float(q[1])))
    zt=[tz(*pts[k]) for k in range(4)]
    if any(z is None for z in zt): continue
    rev=top-zt[1]
    log.append((float(s),round(float(ob),2),round(top,3),round(rev,3)))
    rows.append((s,pts,top,zt,rev))
bm=bmesh.new(); G=[]
for s,pts,top,zt,rev in rows:
    f=lambda t: t*t*(3-2*t)
    z=[top-0.01]
    for k,w in ((1,0.25),(2,0.65),(3,1.0)):
        zz=(top-0.01)*(1-f(w))+(zt[k]-0.01)*f(w); z.append(max(zz,zt[k]-0.01) if rev>0.02 else zt[k]-0.01)
    G.append([bm.verts.new((pts[k][0],pts[k][1],z[k])) for k in range(4)])
for i in range(len(G)-1):
    for j in range(3): bm.faces.new((G[i][j],G[i+1][j],G[i+1][j+1],G[i][j+1]))
mats=[m for m in bpy.data.materials if any(k in m.name.lower() for k in ('verge','lawn','grass','turf'))]
pref=[m for m in mats if 'WS73' in m.name]+[m for m in mats if 'lawn' in m.name.lower()]+mats
mat=pref[0] if pref else None
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me2=bpy.data.meshes.new('WS106_CollegeAve_W_curb_back_lawn_backfill'); bm.to_mesh(me2); bm.free()
for p in me2.polygons: p.use_smooth=True
if mat: me2.materials.append(mat)
o2=O.new(me2.name,me2); cb.users_collection[0].objects.link(o2)
mx=max([r[4] for r in rows] or [0])
print('C106 rows',len(rows),'faces',len(me2.polygons),'mat',mat.name if mat else None,'max reveal %.3f'%mx)
for x in log: print('C106',x)
json.dump(dict(rows=len(rows),mat=mat.name if mat else None,log=log),open('/workspace/nj-scenes/montclair-state/scripts/ws106/curbback106.json','w'))
if os.environ.get('SAVE')=='1' and rows and mat: bpy.ops.wm.save_mainfile(); print('C106 SAVED')

# ws130 self-review fix: my LiDAR facade line was read 2.7 m too far W; the model S-wing E wall (x=-197.43+0.2433(y+227),
# raycast) matches the LiDAR class-6 eave edge (-193 @-212, -195 @-220, -197 @-226) less the 0.7 m eave. -> trim drive faces
# >0.3 m inside the wall, rebuild the ladder hatch against the real wall (it had landed inside the building).
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
xFm=lambda y:-197.43+(y+227.0)*0.2433
dr=[o for o in bpy.data.objects if o.name.startswith('WS130_Chapin_E_service_drive')][0]
bm=bmesh.new(); bm.from_mesh(dr.data)
kill=[f for f in bm.faces if f.normal.z<0.5]
k2=[f for f in bm.faces if f.normal.z>=0.5 and all(v.co.y>-229.4 and v.co.x<xFm(v.co.y)-0.3 for v in f.verts)]
bmesh.ops.delete(bm,geom=kill+k2,context='FACES'); bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
for ed in [ed for ed in bm.edges if ed.is_boundary]:
    a,b=ed.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
bm.to_mesh(dr.data); bm.free(); dr.data.update(); print('M130b drive faces inside wall removed',len(k2))
TD=BVHTree.FromPolygons([v.co for v in dr.data.vertices],[p.vertices for p in dr.data.polygons if p.normal.z>0.5])
po=[o for o in bpy.data.objects if o.name.startswith('WS130_stall_lines')][0]
pm=po.data.materials[0]
# keep the stall lines (x > -193), drop the old hatch, rebuild hatch
pb=bmesh.new(); pb.from_mesh(po.data)
bmesh.ops.delete(pb,geom=[f for f in pb.faces if f.calc_center_median().x<-192.8],context='FACES')
bmesh.ops.delete(pb,geom=[v for v in pb.verts if not v.link_faces],context='VERTS')
def zp(x,y):
    h=TD.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; return None if h is None else h.z
def strip(p0,p1,w):
    p0=Vector(p0); p1=Vector(p1); d=(p1-p0); L=d.length; d.normalize(); nn=Vector((-d.y,d.x))*w/2; n=max(1,int(L/0.5)); r=[]
    for i in range(n+1):
        q=p0+d*(L*i/n); pair=[]
        for s in (-1,1):
            u=q+nn*s; z=zp(u.x,u.y)
            if z is None: return
            pair.append((u.x,u.y,z+0.006))
        r.append(pair)
    vv=[[pb.verts.new(p) for p in pair] for pair in r]
    for i in range(n): pb.faces.new((vv[i][0],vv[i+1][0],vv[i+1][1],vv[i][1]))
n0=len(pb.faces)
for y in np.arange(-221.4,-229.6,-0.9):
    a=xFm(y)+0.2; strip((a,y),(a+1.8,y-0.35),0.30)
for off in (0.2,2.0):
    strip((xFm(-221.0)+off,-221.0),(xFm(-229.6)+off,-229.6),0.10)
pb.normal_update(); pb.to_mesh(po.data); pb.free(); po.data.update(); print('M130b hatch faces',len(po.data.polygons)-n0)
if SAVE: bpy.ops.wm.save_mainfile(); print('M130b SAVED')

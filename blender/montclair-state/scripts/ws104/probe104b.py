import bpy,numpy as np,sys,json
from mathutils import Vector
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws104'); from frame104 import *
p0,_=frame(-24); p1,_=frame(3)
x0,x1=min(p0[0],p1[0])-12,max(p0[0],p1[0])+12; y0,y1=min(p0[1],p1[1])-12,max(p0[1],p1[1])+12
print('P104b box',x0,x1,y0,y1)
res=[]
for ob in bpy.data.objects:
    if ob.type!='MESH' or ob.name.startswith('T_') or ob.name.startswith('Terrain') or ob.name.startswith('Context'): continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: continue
    me=ob.data; n=len(me.vertices)
    if n==0 or n>2_000_000: continue
    c=np.empty(n*3,dtype=np.float32); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world,dtype=np.float32); W=c@M[:3,:3].T+M[:3,3]; del c
    m=(W[:,0]>x0)&(W[:,0]<x1)&(W[:,1]>y0)&(W[:,1]<y1)
    if not m.any(): continue
    pts=[]
    for q in W[m]:
        s,o=so(q)
        if -24<=s<=3 and -4<=o<=10: pts.append((round(float(s),2),round(o,2),round(float(q[2]),3)))
    if pts: res.append({'name':ob.name,'hide_render':ob.hide_render,'n':len(pts),'pts':pts[:20000]})
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws104/probe104b.json','w'))
for r in res: print('P104',r['name'],r['hide_render'],r['n'])

import bpy,numpy as np,sys,json
from mathutils import Vector
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws103'); from frame103 import *
res=[]
for ob in bpy.data.objects:
    if ob.type!='MESH': continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<-235 or min(xs)>-195 or max(ys)<-185 or min(ys)>-140: continue
    me=ob.data; n=len(me.vertices)
    if n==0: continue
    c=np.empty(n*3,dtype=np.float32); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world,dtype=np.float32); W=c@M[:3,:3].T+M[:3,3]; del c
    m=(W[:,0]>-235)&(W[:,0]<-195)&(W[:,1]>-185)&(W[:,1]<-140)
    if not m.any(): continue
    pts=[]
    for q in W[m][::max(1,int(m.sum())//400)]:
        s,o=so(q)
        if -14<=s<=5 and -3<=o<=11: pts.append((round(float(s),2),round(o,2),round(float(q[2]),3)))
    if pts: res.append({'name':ob.name,'hide_render':ob.hide_render,'n':len(pts),'pts':pts})
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws104/probe104.json','w'))
for r in res: print('P104',r['name'],r['hide_render'],r['n'])

import bpy,numpy as np,sys,json
from mathutils import Vector
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws105'); from frame105 import *
p0,_=frame(-2); p1,_=frame(42); print('P105 frame ends',p0,p1)
X0,X1=min(p0[0],p1[0])-20,max(p0[0],p1[0])+20; Y0,Y1=min(p0[1],p1[1])-20,max(p0[1],p1[1])+20
res=[]
for ob in bpy.data.objects:
    if ob.type!='MESH': continue
    bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    me=ob.data; n=len(me.vertices)
    if n==0: continue
    c=np.empty(n*3,dtype=np.float32); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world,dtype=np.float32); W=c@M[:3,:3].T+M[:3,3]; del c
    m=(W[:,0]>X0)&(W[:,0]<X1)&(W[:,1]>Y0)&(W[:,1]<Y1)
    if not m.any(): continue
    idx=np.where(m)[0]; idx=idx[::max(1,len(idx)//1500)]; pts=[]
    for q in W[idx]:
        s,o=so(q)
        if -2<=s<=42 and 6.5<=o<=18: pts.append((round(float(s),2),round(o,2),round(float(q[2]),3)))
    if pts: res.append({'name':ob.name,'hide':ob.hide_render,'mats':[mm.name for mm in me.materials if mm],'n':len(pts),'zr':[min(p[2] for p in pts),max(p[2] for p in pts)],'sr':[min(p[0] for p in pts),max(p[0] for p in pts)],'or':[min(p[1] for p in pts),max(p[1] for p in pts)],'coll':ob.users_collection[0].name})
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws105/probe105.json','w'))
for r in res: print('P105',r['name'],r['hide'],r['n'],r['zr'],r['sr'],r['or'],r['mats'][:3],r['coll'])

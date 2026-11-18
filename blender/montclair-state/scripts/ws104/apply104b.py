# ws104b: lawn behind the tapered W curb end N of the table re-seated LiDAR-relative (raise-only), so the curb back and the walk N end
# no longer stand proud of a sunken lawn. Target z = model road edge z(s) + (LiDAR(s,o) - LiDAR(s,3.0)); faded out by o 9.5 / s -9.
import bpy,numpy as np,sys,os,json
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws104'); from frame104 import *
def sm(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
L=np.load('/workspace/nj-scenes/montclair-state/scripts/ws102/lid_so.npz'); ls,lo,lz=L['s'],L['o'],L['z']
def lid(s,o,r=0.45):
    m=(np.abs(ls-s)<r)&(np.abs(lo-o)<r); return float(np.median(lz[m])) if m.any() else None
def getW(ob):
    me=ob.data; n=len(me.vertices); c=np.empty(n*3); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world); return c@M[:3,:3].T+M[:3,3], M
BOX=(-235,-200,-175,-140)
road=[o for o in bpy.data.objects if o.name.startswith('WS27_CollegeAve_carriageway')][0]
RW,_=getW(road); ri=np.where((RW[:,0]>BOX[0])&(RW[:,0]<BOX[1])&(RW[:,1]>BOX[2])&(RW[:,1]<BOX[3]))[0]
rso=np.array([so(RW[k]) for k in ri]); edge=rso[:,1]>2.5
def zedge(s):
    d=np.abs(rso[edge,0]-s); k=np.argsort(d)[:2]; return float(RW[ri[edge][k],2].mean())
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; TW,TM=getW(T)
ti=np.where((TW[:,0]>BOX[0])&(TW[:,0]<BOX[1])&(TW[:,1]>BOX[2])&(TW[:,1]<BOX[3]))[0]; nr=0; mx=0; log=[]
for k in ti:
    s,o=so(TW[k])
    if not (-9.0<=s<=0.2 and 3.5<=o<=9.5): continue
    a=lid(s,o); b=lid(s,3.0)
    if a is None or b is None: continue
    tgt=zedge(min(s,-0.05))+(a-b)-0.015
    w=(1-sm(7.5,9.5,o))*(1-sm(-9.0,-7.0,-s+0.0) if False else 1-sm(7.0,9.0,-s))
    nz=TW[k,2]+max(0.0,tgt-TW[k,2])*w
    if s>-0.8 and o<6.8: nz=min(nz,max(TW[k,2],124.915))
    if nz>TW[k,2]+1e-4: mx=max(mx,nz-TW[k,2]); log.append((round(s,2),round(o,2),round(TW[k,2],3),round(nz,3))); TW[k,2]=nz; nr+=1
Mi=np.linalg.inv(TM); T.data.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); T.data.update()
rep={'raised':nr,'max':mx,'log':log}; json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws104/apply104b.json','w'))
print('B104 raised',nr,'max',round(mx,3)); [print('B104',x) for x in log[:40]]
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('B104 SAVED')

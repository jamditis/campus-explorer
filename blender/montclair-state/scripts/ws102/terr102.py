import bpy,numpy as np,os,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src=open('/workspace/nj-scenes/montclair-state/scripts/ws102/apply102.py').read(); exec(src[:src.index('mats={')])
lg=np.load(B+'lidgrid102.npz'); LG=lg['G']; GX,GY,GR=float(lg['X0']),float(lg['Y0']),float(lg['R'])
SSf=np.arange(-1,S1+1.01,0.5); FR=[frame(s) for s in SSf]; PP=np.array([f[0] for f in FR]); NN=np.array([f[1] for f in FR])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.data; nt=len(tm.vertices)
c2=np.empty(nt*3); tm.vertices.foreach_get('co',c2); c2=c2.reshape(-1,3); MT=np.array(T.matrix_world); TW=c2@MT[:3,:3].T+MT[:3,3]
sel=np.where((TW[:,0]>-268)&(TW[:,0]<-195)&(TW[:,1]>-252)&(TW[:,1]<-150))[0]
# objects to protect: do not lift terrain into building footprints (only use LiDAR class-2 cells, which exclude roofs)
vs=[];tris=[]
for o in bpy.data.objects:
    if o.name.startswith(('WS102_CollegeAve_S_carriageway','WS102_CollegeAve_S_curb')):
        b0=len(vs); vs+=[o.matrix_world@v.co for v in o.data.vertices]; tris+=[[b0+i for i in p.vertices] for p in o.data.polygons]
bvh=BVHTree.FromPolygons(vs,tris)
mv=0;dz=[];cap=0
for k in sel:
    q=TW[k,:2]; dd=np.hypot(*(PP-q).T); a=int(np.argmin(dd)); s=SSf[a]
    if s<0.5 or s>S1+0.5: continue
    o=(q-PP[a])@NN[a]; e=eE(s)
    d_out=max(e-o, o-EW, 0.0)    # distance outside the road edge
    if d_out>6.0: continue
    w=1.0 if d_out<3.0 else 1.0-(d_out-3.0)/3.0; w=w*w*(3-2*w)
    i=int(round((q[0]-GX)/GR)); j=int(round((q[1]-GY)/GR))
    if not(1<=j<LG.shape[0]-1 and 1<=i<LG.shape[1]-1): continue
    v=LG[j-1:j+2,i-1:i+2]; v=v[np.isfinite(v)]
    if len(v)<2: continue
    t=float(np.median(v))-0.01
    if abs(TW[k,2]-t)>0.04 and abs(TW[k,2]-t)<2.0:
        dz.append(t-TW[k,2]); TW[k,2]+= (t-TW[k,2])*w; mv+=1
    h=bvh.ray_cast(Vector((q[0],q[1],TW[k,2]+6)),Vector((0,0,-1)),14)
    if h[0] is not None and TW[k,2]>h[0].z-0.05: TW[k,2]=h[0].z-0.05; cap+=1
Mi=np.linalg.inv(MT); tm.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); tm.update()
dz=np.array(dz) if dz else np.zeros(1)
print('R102 terrain re-seated',mv,'dz med %.2f p5 %.2f p95 %.2f'%(np.median(dz),np.percentile(dz,5),np.percentile(dz,95)),'capped',cap)
# move shared trees standing on moved ground by origin? report trees in corridor
json.dump(dict(moved=mv,cap=cap,dz_med=float(np.median(dz)),dz_p5=float(np.percentile(dz,5)),dz_p95=float(np.percentile(dz,95))),open(B+'terr102.json','w'))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('R102 SAVED')

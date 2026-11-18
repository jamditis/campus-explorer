# ws104: College Ave table N-edge joint. Evidence: 2023 LiDAR (ws102 lid_so.npz) is flat across the road + W verge at s 0..1 and shows the
# W curb step (~0.12 m at s -4) fading out by s ~-1.5; OSM footway 232846679 (the W sidewalk) reaches the table N edge at s 0 and turns E
# across the road there; OSM College Ave N of the table: sidewalk:left=no (W side = curb + lawn). So: road ramps flush into the table,
# curbs taper to flush, W walk ends at the table N edge, sunken old Footpaths stub retired, lawn behind the curb end raised to meet it.
import bpy,bmesh,numpy as np,sys,os,json
from mathutils import Vector
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws104'); from frame104 import *
def sm(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
ZT=124.93; rep={}
def getW(ob):
    me=ob.data; n=len(me.vertices); c=np.empty(n*3); me.vertices.foreach_get('co',c); c=c.reshape(-1,3)
    M=np.array(ob.matrix_world); return c@M[:3,:3].T+M[:3,3], M
def setW(ob,W,M):
    Mi=np.linalg.inv(M); ob.data.vertices.foreach_set('co',(W@Mi[:3,:3].T+Mi[:3,3]).ravel()); ob.data.update()
def SO(W,box):
    idx=np.where((W[:,0]>box[0])&(W[:,0]<box[1])&(W[:,1]>box[2])&(W[:,1]<box[3]))[0]
    so_=np.array([so(W[k]) for k in idx]) if len(idx) else np.zeros((0,2)); return idx,so_
BOX=(-235,-200,-175,-145)
road=[o for o in bpy.data.objects if o.name.startswith('WS27_CollegeAve_carriageway')][0]
RW,RM=getW(road); ri,rso=SO(RW,BOX)
m0=rso[:,0]>-0.3; fit=np.polyfit(rso[m0,1],RW[ri[m0],2],1); rep['fit']=list(fit)
def dz(s,o): return np.maximum(0,ZT-np.polyval(fit,np.clip(o,-3.3,3.3)))*sm(-4,0,s)
# original road z lookup for curb bases
rs_orig=rso.copy(); rz_orig=RW[ri,2].copy()
def zroad0(s,o):
    d=(rs_orig[:,0]-s)**2+((rs_orig[:,1]-o)*0.4)**2; k=np.argsort(d)[:3]; w=1/(np.sqrt(d[k])+1e-3); return float((rz_orig[k]*w).sum()/w.sum())
sel=(rso[:,0]>-4.2)&(rso[:,0]<0.4); RW[ri[sel],2]+=dz(rso[sel,0],rso[sel,1]); setW(road,RW,RM); rep['road_verts']=int(sel.sum())
for nm in ('WS27_CollegeAve_curb_right','WS27_CollegeAve_curb_left'):
    cb=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; CW,CM=getW(cb); ci,cso=SO(CW,BOX); n=0
    for k,(s,o) in zip(ci,cso):
        if not (-4.2<s<0.4): continue
        oc=np.clip(o,-3.2,3.3); zb=zroad0(s,oc); h=CW[k,2]-zb
        CW[k,2]+=float(dz(s,oc))-max(h,0)*float(sm(-3.5,-0.3,s)); n+=1
    setW(cb,CW,CM); rep[nm]=n
# retire sunken Footpaths_OSM stub at the joint (s -2..1.3, o -3.4..7.5)
fp=bpy.data.objects['Footpaths_OSM']; bm=bmesh.new(); bm.from_mesh(fp.data); mw=fp.matrix_world; dl=[]
for f in bm.faces:
    c=mw@f.calc_center_median()
    if not (BOX[0]<c.x<BOX[1] and BOX[2]<c.y<BOX[3]): continue
    s,o=so(np.array([c.x,c.y]))
    if -2.0<=s<=1.3 and -3.4<=o<=7.5: dl.append(f)
bmesh.ops.delete(bm,geom=dl,context='FACES'); lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
bm.to_mesh(fp.data); fp.data.update(); bm.free(); rep['fp_removed']=len(dl)
# extend WS103 walk N end from s 1 to s 0 (flush with the table N edge / tapered curb end)
wk=[o for o in bpy.data.objects if o.name.startswith('WS103_CollegeAve_S_W_sidewalk')][0]
bm=bmesh.new(); bm.from_mesh(wk.data); mw=wk.matrix_world; mi=mw.inverted()
VS={v:so(np.array((mw@v.co)[:2])) for v in bm.verts}
end=[f for f in bm.faces if all(abs(VS[v][0]-1.0)<0.1 for v in f.verts)]
bmesh.ops.delete(bm,geom=end,context='FACES_ONLY'); lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
row=[v for v in bm.verts if abs(VS[v][0]-1.0)<0.1]; byo={}
for v in row:
    k=round(VS[v][1],1)
    if k not in byo or (mw@v.co).z>(mw@byo[k].co).z: byo[k]=v
top=[byo[k] for k in sorted(byo)]; rep['top_row']=[(round(VS[v][1],2),round((mw@v.co).z,3)) for v in top]
G=[top]
for s in (0.5,0.0):
    p,n=frame(s); r=[]
    for v in top:
        o=VS[v][1]; z=(mw@v.co).z+0.031*(1-s); r.append(bm.verts.new(mi@Vector((*(p+n*o),z))))
    G.append(r)
for i in range(2):
    for j in range(len(top)-1): bm.faces.new((G[i][j],G[i][j+1],G[i+1][j+1],G[i+1][j]))
    a,b=G[i][-1],G[i+1][-1]; a2=bm.verts.new(a.co-Vector((0,0,0.5))); b2=bm.verts.new(b.co-Vector((0,0,0.5))); bm.faces.new((a,b,b2,a2))
for j in range(len(top)-1):
    a,b=G[2][j],G[2][j+1]; a2=bm.verts.new(a.co-Vector((0,0,0.3))); b2=bm.verts.new(b.co-Vector((0,0,0.3))); bm.faces.new((a,b,b2,a2))
for f in bm.faces:
    f.smooth=False
    if f.normal.z<-0.5: f.normal_flip()
bm.normal_update()
for f in bm.faces:
    if f.normal.z<-0.5: f.normal_flip()
bm.to_mesh(wk.data); wk.data.update(); bm.free()
# terrain: cap under new walk strip; raise lawn behind the tapered curb end (s -4..0, o 3.5..8) to meet curb top / walk (raise-only)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; TW,TM=getW(T); ti,tso=SO(TW,BOX); nc=nr=0
for k,(s,o) in zip(ti,tso):
    if -0.1<=s<=1.2 and 3.0<=o<=6.7:
        lim=ZT-0.04-0.03*s
        if TW[k,2]>lim: TW[k,2]=lim; nc+=1
    elif -4.5<=s<0 and 3.55<=o<=8.5:
        oc=3.3; zb=zroad0(s,oc); ztop=zb+float(dz(s,oc))+0.16*(1-float(sm(-3.5,-0.3,s)))
        lim=ztop-0.03-max(0,o-4.0)/4.0
        w=1-float(sm(-4.5,-3.5,-s-0.0)) if False else 1.0
        if TW[k,2]<lim: TW[k,2]=lim; nr+=1
setW(T,TW,TM); rep['terr_cap']=nc; rep['terr_raise']=nr
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws104/apply104.json','w'),default=float); print('A104',rep)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A104 SAVED')

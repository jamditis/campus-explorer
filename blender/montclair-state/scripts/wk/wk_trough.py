"""wk: fill the trough along the Stone footway's west edge (verge between service road 546643370 and footway 546643369,
y~252-276). Ground in the verge raised (raise-only) to a straight cross-slope from road top -3 cm to footway top -2.5 cm;
verts just under the footway edge lifted to slab -5 cm; y-faded at both ends; only the top-most ground sheet moves."""
import bpy,numpy as np,sys,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
Y0,Y1,FADE=252.0,277.0,2.5
def bvh(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
def z(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
F=[bvh(O['QS_footway_546643369_UNVERIFIED']),bvh(O['QW_footway_546643369_ext_UNVERIFIED'])]; R=bvh(O['QS_service_546643370_UNVERIFIED'])
def fz(x,y):
    v=[z(b,x,y) for b in F]; v=[a for a in v if a is not None]; return max(v) if v else None
GN=['QW_DTM_north_edge_ramp_UNVERIFIED','Terrain_LiDAR_DTM_1m','WV_stone_west_LiDAR_patch_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED']
GB={n:bvh(O[n]) for n in GN}
def gtop(x,y):
    v=[z(b,x,y) for b in GB.values()]; v=[a for a in v if a is not None]; return max(v) if v else None
edge={}
def edges(y):
    k=round(y,1)
    if k in edge: return edge[k]
    xs=np.arange(115,152,0.05); fx=[x for x in xs if fz(x,k) is not None]
    if not fx: edge[k]=None; return None
    fw=min(fx); rx=[x for x in xs if x<fw and z(R,x,k) is not None]
    if not rx: edge[k]=None; return None
    re=max(rx); edge[k]=(re,fw,z(R,re-0.05,k),fz(fw+0.05,k)); return edge[k]
WL=[]
def stats(tag):
    e=[]; WL.clear()
    for y in np.arange(Y0,Y1,0.2):
        E=edges(y)
        if not E: continue
        for x in np.arange(E[1]-0.45,E[1],0.1):
            g=gtop(x,y)
            if g is not None: e.append(E[3]-g); WL.append((round(float(x),1),round(float(y),1),round(E[3]-g,3)))
    W=sorted(W,key=lambda a:-a[2])[:6] if 'W' in dir() else []
    e=np.array(e); r=dict(n=len(e),p50=round(float(np.median(e)),3),p90=round(float(np.percentile(e,90)),3),max=round(float(e.max()),3)); print('EXP',tag,r,sorted(WL,key=lambda a:-a[2])[:8],flush=True); return r
def zfc():
    zf=0
    for y in np.arange(Y0,Y1,0.25):
        for x in np.arange(118,146,0.25):
            v=sorted([a for a in [z(b,x,y) for b in GB.values()] if a is not None])
            if len(v)>1 and v[-1]-v[-2]<0.003: zf+=1
    return zf
print('ZF0',zfc(),flush=True)
rep={'before':stats('before')}
PRE={}
for n in GN:
    o=O[n]; mw=o.matrix_world; mi=mw.inverted(); cnt=0; mx=0; PRE[n]=[v.co.z for v in o.data.vertices]
    for v in o.data.vertices:
        c=mw@v.co
        if not (Y0<=c.y<=Y1 and 118<=c.x<=146): continue
        E=edges(c.y)
        if not E: continue
        re,fw,rz,fzz=E
        if not (re-0.05<=c.x<=fw+2.0): continue
        g=gtop(c.x,c.y)
        if g is not None and c.z<g-0.02: continue   # not the top sheet here
        if c.x>=fw:
            sz=fz(c.x,c.y)
            if sz is None: continue
            tgt=sz-0.06
        else:
            t=(c.x-re)/max(fw-re,0.3); t=min(max(t,0),1)
            tgt=(rz-0.03)*(1-t)+(fzz-0.045)*t
            rh=z(R,c.x,c.y)
            if rh is not None: tgt=min(tgt,rh-0.05)
        w=min(1.0,(c.y-Y0)/FADE,(Y1-c.y)/FADE); w=w*w*(3-2*w)
        dz=min(max(0.0,(tgt-c.z)*w),0.36)
        if dz>0.002: c.z+=dz; v.co=mi@c; cnt+=1; mx=max(mx,dz)
    o.data.update(); rep[n]=[cnt,round(mx,3)]; print('RAISE',n,cnt,round(mx,3),flush=True)
bpy.context.view_layer.update(); GB={n:bvh(O[n]) for n in GN}
rep['after']=stats('after')
# pokes above slabs / road
pk=0; PK=[]
for y in np.arange(Y0,Y1,0.2):
    for x in np.arange(118,146,0.2):
        s=fz(x,y); r=z(R,x,y); g=gtop(x,y)
        if g is None: continue
        if s is not None and g>s-0.005: pk+=1; PK.append(('F',round(float(x),1),round(float(y),1),round(g-s,3)))
        if r is not None and g>r-0.005: pk+=1; PK.append(('R',round(float(x),1),round(float(y),1),round(g-r,3)))
for it in range(3):
    if not PK: break
    for n in GN:
        o=O[n]; mw=o.matrix_world; me=o.data; B=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); ids={}
        for kind,x,y,d in PK:
            h=B.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
            if h[2] is None: continue
            for vi in me.polygons[h[2]].vertices:
                if me.vertices[vi].co.z>PRE[n][vi]+1e-5: ids[vi]=max(ids.get(vi,0),d+0.015)
        for vi,d in ids.items(): me.vertices[vi].co.z=max(PRE[n][vi],me.vertices[vi].co.z-d)
        me.update()
    bpy.context.view_layer.update(); GB={n:bvh(O[n]) for n in GN}; pk=0; PK=[]
    for y in np.arange(Y0,Y1,0.2):
        for x in np.arange(118,146,0.2):
            s_=fz(x,y); r=z(R,x,y); g=gtop(x,y)
            if g is None: continue
            if s_ is not None and g>s_-0.005: pk+=1; PK.append(('F',round(float(x),1),round(float(y),1),round(g-s_,3)))
            if r is not None and g>r-0.005: pk+=1; PK.append(('R',round(float(x),1),round(float(y),1),round(g-r,3)))
    print('BACKOFF',it,pk,PK[:8],flush=True)
rep['after2']=stats('after2')
rep['pokes']=pk; print('POKES',pk,PK[:20],flush=True)
# z-fight: two sheets within 3 mm
zf=0
for y in np.arange(Y0,Y1,0.25):
    for x in np.arange(118,146,0.25):
        v=sorted([a for a in [z(b,x,y) for b in GB.values()] if a is not None])
        if len(v)>1 and v[-1]-v[-2]<0.003: zf+=1
rep['zfight']=zf; print('ZF',zf,flush=True)
# grass re-snap + soil strip reseat
SL=F+[R]; kg=0
for gobj in [o for o in O if o.type=='MESH' and 'grass_points' in o.name]:
    m=gobj.matrix_world; mi2=m.inverted(); ch=False
    for v in gobj.data.vertices:
        c=m@v.co
        if not (Y0-0.5<=c.y<=Y1+0.5 and 117<=c.x<=147): continue
        g=gtop(c.x,c.y)
        if g is None: continue
        if any(z(b,c.x,c.y) is not None for b in SL): continue
        if abs(c.z-g)>0.01: c.z=g; v.co=mi2@c; kg+=1; ch=True
    if ch: gobj.data.update()
rep['grass']=kg; print('GRASS',kg,flush=True)
t=O.get('QT_soil_edge_546643369_UNVERIFIED'); k=0
if t:
    mw=t.matrix_world; inv=mw.inverted(); S=F[0]
    for v in t.data.vertices:
        w=mw@v.co
        if not (Y0-0.5<=w.y<=Y1+0.5) or S.find_nearest(w)[3]<0.05: continue
        g=gtop(w.x,w.y)
        if g is not None and abs(w.z-(g+0.005))>0.003: v.co=inv@Vector((w.x,w.y,g+0.005)); k+=1
    t.data.update()
rep['soil']=k; print('SOIL',k,flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/data/wk/trough_report.json','w'),indent=1)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O),flush=True)

# ws116: UNIFY #20 - Chapin W entrance plaza at the WS115 walk N end + N connector walk + 2 mulch beds (2020 ortho trace, DTM 2023 grade)
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
def sdtm(x,y): return float(np.mean([dtm(x+dx,y+dy) for dx in (-1.5,0,1.5) for dy in (-1.5,0,1.5)]))
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
# curb E back edge + top
cb=O('WS102_CollegeAve_S_curb_E'); mw=cb.matrix_world
CV=np.array([tuple(mw@v.co) for v in cb.data.vertices]); CV=CV[(CV[:,1]>-206)&(CV[:,1]<-176)]
from mathutils.bvhtree import BVHTree as _B
_cbv=_B.FromPolygons([tuple(mw@v.co) for v in cb.data.vertices],[tuple(p.vertices) for p in cb.data.polygons])
def curb(y):
    m=CV[np.abs(CV[:,1]-y)<0.6]
    if len(m)==0: return None
    # back edge: the curb's E boundary at this y (fit x along the slanted curb: x - 0.35*(y - yv) )
    xb=float(np.max(m[:,0]-0.354*(m[:,1]-y)))
    h=_cbv.ray_cast(Vector((xb-0.06,y,200)),Vector((0,0,-1)),150)
    zt=h[0].z if h[0] is not None else float(m[:,2].max())
    return xb, zt
for y in (-204,-202,-198,-194,-190,-186,-182,-178): print('M116 curb',y,curb(y))
# walk end row
wk=O('WS115_E_walk_N'); wv=wk.data.vertices; mww=wk.matrix_world
WE=np.array([tuple(mww@wv[i].co) for i in range(345,350)]); print('M116 walk end',WE.round(3).tolist())
wmid=WE[2]; woff=float(wmid[2]-(sdtm(wmid[0],wmid[1])+0.05)); print('M116 walk-end offset',round(woff,3))
def zf(x,y):
    z=sdtm(x,y)+0.05
    dw=np.hypot(x-wmid[0],y-wmid[1]); u=np.clip(1-dw/4.0,0,1); u=u*u*(3-2*u); z+=woff*u
    c=curb(y)
    if c:
        dc=x-c[0]
        if dc<1.5:
            v=np.clip(1-dc/1.5,0,1); v=v*v*(3-2*v); z=z*(1-v)+(c[1]-0.004)*v
    return z
mc=O('WS111_CollegeAve_S_E_walk_gap').active_material
mm=O('WS105_Chapin_E_bank_planting_bed_MULCH').active_material
col=bpy.data.collections.new('WS116_Chapin_W_entrance_plaza'); bpy.context.scene.collection.children.link(col)
def quadgrid(c00,c10,c11,c01,nu,nv,lift=0.0,zfn=zf,skirt=0.3,wx=None):
    # bilinear patch c00(SW) c10(SE) c11(NE) c01(NW)
    P=lambda u,v: np.array(c00)*(1-u)*(1-v)+np.array(c10)*u*(1-v)+np.array(c11)*u*v+np.array(c01)*(1-u)*v
    bm=bmesh.new(); G=[]
    for i in range(nv+1):
        r=[]
        for j in range(nu+1):
            x,y=P(j/nu,i/nv)
            if wx is not None:
                xl0,yl=P(0,i/nv); xr,yr=P(1,i/nv); xl=wx(yl) or xl0; x=xl+(j/nu)*(xr-xl)
            r.append(bm.verts.new((x,y,zfn(x,y)+lift)))
        G.append(r)
    for i in range(nv):
        for j in range(nu): bm.faces.new((G[i][j],G[i][j+1],G[i+1][j+1],G[i+1][j]))
    ring=[G[0][j] for j in range(nu+1)]+[G[i][nu] for i in range(1,nv+1)]+[G[nv][j] for j in range(nu-1,-1,-1)]+[G[i][0] for i in range(nv-1,0,-1)]
    if skirt:
        lo=[bm.verts.new((v.co.x,v.co.y,v.co.z-skirt)) for v in ring]
        for k in range(len(ring)):
            k2=(k+1)%len(ring); bm.faces.new((ring[k],ring[k2],lo[k2],lo[k]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if sum(f.normal.z*f.calc_area() for f in bm.faces if abs(f.normal.z)>0.5)<0: bmesh.ops.reverse_faces(bm,faces=bm.faces)
    return bm
def link(name,bm,mat):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
yS,yN=-202.3,-192.3
yS2=-203.3  # plaza S edge pulled S under the WS115 walk end row (walk sits 6 mm on top)
cS=curb(yS2)[0]; cN=curb(yN)[0]
xc=lambda y: -220.05+0.30*(y+192.3)
xeN=xc(yN)+1.25
NEW=[]
NEW.append(link('WS116_Chapin_W_plaza_concrete_ortho2020_DTM2023_UNVERIFIEDgrade',quadgrid((cS,yS2),(-218.55,yS2),(xeN,yN),(cN,yN),18,22,wx=lambda y:(curb(y) or (None,))[0]),mc))
eW=lambda y: -218.55+(y-yS2)*(xeN+218.55)/(yN-yS2)
def zcor(x,y):
    x0=eW(y); return zf(x0,y)+0.05*max(0.0,x-x0)
NEW.append(link('WS116_Chapin_W_plaza_E_corridor_concrete_5pct_to_entry_ortho2020_UNVERIFIED',quadgrid((eW(-200.4),-200.4),(-212.2,-200.3),(-212.2,-196.9),(eW(-196.7),-196.7),8,6,zfn=zcor),mc))
NEW.append(link('WS116_Chapin_W_N_connector_walk_concrete_2p5m_ortho2020_UNVERIFIED',quadgrid((xc(yN)-1.25,yN),(xc(yN)+1.25,yN),(xc(-182.0)+1.25,-182.0),(xc(-182.0)-1.25,-182.0),5,22),mc))
zb=lambda x,y: zf(min(x,-215.5),y)-0.05
cB=curb(-186)[0]+0.33*(-182.0+186)
NEW.append(link('WS116_Chapin_W_bed_W_mulch_ortho2020_UNVERIFIED',quadgrid((cN+0.02,yN),(xc(yN)-1.25,yN),(xc(-182.0)-1.25,-182.0),(cB+0.02,-182.0),6,20,zfn=zb,skirt=0.15,wx=lambda y:(curb(y)[0]+0.02 if (curb(y) and y<-184.5) else -222.1+0.33*(y+186)+0.02)),mm))
eE=lambda y: -214.6+(y+196.9)*(1.6/14.9)
NEW.append(link('WS116_Chapin_W_bed_E1_mulch_ortho2020_UNVERIFIED',quadgrid((eW(-196.7),-196.7),(eE(-196.7),-196.7),(eE(yN),yN),(xeN,yN),6,8,zfn=zb,skirt=0.15),mm))
NEW.append(link('WS116_Chapin_W_bed_E2_mulch_ortho2020_UNVERIFIED',quadgrid((xeN,yN),(eE(yN),yN),(eE(-182.0),-182.0),(xc(-182.0)+1.25,-182.0),6,20,zfn=zb,skirt=0.15),mm))
for o in NEW:
    for p in o.data.polygons: p.use_smooth=False
    zs=[ (o.matrix_world@v.co).z-dtm(*(o.matrix_world@v.co)[:2]) for v in o.data.vertices][:200]
    print('M116 new',o.name,'faces',len(o.data.polygons),'dz %.2f..%.2f'%(min(zs),max(zs)))
# terrain: push under paving/beds, lift at edges
tops=[];planes=[]
for o in NEW:
    me=o.data
    for f in me.polygons:
        if f.normal.z<0.7: continue
        vs=[me.vertices[i].co.copy() for i in f.vertices]; tops.append([Vector((v.x,v.y,0)) for v in vs]); planes.append((vs[0],f.normal.copy()))
vv=[];pp=[]
for t in tops: b=len(vv); vv+=t; pp.append(list(range(b,b+len(t))))
bvh=BVHTree.FromPolygons(vv,pp)
def zat(i,x,y): p0,nn=planes[i]; return p0.z-(nn.x*(x-p0.x)+nn.y*(y-p0.y))/nn.z
for pn in ('WS113_terrain_fan_fill','WS110_ground_patch','Terrain_LiDAR_DTM_1m'):
    try: o=O(pn)
    except StopIteration: continue
    m2=o.data; mw2=o.matrix_world; inv=mw2.inverted(); nl=nd=0; mx=0
    for v in m2.vertices:
        w=mw2@v.co
        if not (-232<w.x<-210 and -206<w.y<-178): continue
        loc,nor,idx,dd=bvh.find_nearest(Vector((w.x,w.y,0)),1.3)
        if loc is not None and planes[idx][0].z<0: pass
        if loc is None: continue
        ze2=zat(idx,loc.x,loc.y)
        if dd<0.02:
            if w.z>ze2-0.06: w.z=ze2-0.06; v.co=inv@w; nd+=1
        else:
            tgt=ze2-0.02-0.10*dd
            if dd<1.0 and abs(tgt-w.z)<0.6: mx=max(mx,abs(tgt-w.z)); w.z=tgt; v.co=inv@w; nl+=1
            elif w.z<tgt and tgt-w.z<0.5: mx=max(mx,tgt-w.z); w.z=tgt; v.co=inv@w; nl+=1
    m2.update(); print('M116 lawn',o.name[:30],'lift',nl,'max %.3f'%mx,'down',nd)
pv=bpy.data.objects.get('WS113_paving_tops_proxy')
if pv:
    b2=bmesh.new(); b2.from_mesh(pv.data); n0=len(b2.faces)
    for o in NEW:
        t=bmesh.new(); t.from_mesh(o.data); t.normal_update(); bmesh.ops.delete(t,geom=[f for f in t.faces if f.normal.z<0.5],context='FACES')
        m3=bpy.data.meshes.new('tmp'); t.to_mesh(m3); t.free(); b2.from_mesh(m3); bpy.data.meshes.remove(m3)
    b2.to_mesh(pv.data); b2.free(); pv.data.update(); print('M116 proxy',n0,'->',len(pv.data.polygons))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M116 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M116 SAVED',SAVE)
if os.environ.get('CUT'):
    exec(open(R+'scripts/ws116/cut116.py').read())

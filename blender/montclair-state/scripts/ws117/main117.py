# ws117: UNIFY #22 - Chapin Hall W main entrance (2005-08 Hillier renovation reoriented the entrance to College Ave):
# 11-riser concrete stair from the WS116 forecourt up to an entrance landing at the 2023 LiDAR class-2 level (124.75),
# a landing terrace along the W facade (x -213.x .. -209.1, y -201.3 .. -184.6), low white edge wall, rails, regraded E beds.
import bpy, bmesh, numpy as np, os
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
ZL=124.77            # landing finish (LiDAR class-2 124.73-124.79 on the landing)
XW=-209.1            # into the WS107 block 07 W face (-209.2)
YS=-201.3            # into the WS107 S wing face (-201.2)
XT=-213.4            # top nosing line (LiDAR rise ends -213.3..-213.0)
N=11; T=0.37; XB=XT-(N-1)*T   # bottom riser x = -217.1 (LiDAR rise starts ~ -217.2)
YC=-196.95; CW=0.30           # N cheek wall y -196.95..-196.65 (bed E1 S edge -196.7)
eE=lambda y: -214.6+(y+196.9)*(1.6/14.9)   # WS116 bed E1/E2 E edge
YN=-182.0
xr=lambda y: -213.3+(min(y,-184.0)+196.65)*(2.3/12.65)   # LiDAR 124.5 m contour = real terrace edge (ws117 grid)
mc=O('WS116_Chapin_W_plaza_concrete').active_material
wallm=O('WS105_Chapin_E_bank_stair_cheek_walls_white').active_material
steel=O('WS105_Chapin_E_bank_stair_handrails_steel').active_material
col=bpy.data.collections.get('WS117_Chapin_W_main_entrance') or bpy.data.collections.new('WS117_Chapin_W_main_entrance')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
# 1) compress the WS116 corridor so it ends at the stair foot (keeps its 5 % grade, topology and skirts)
cor=O('WS116_Chapin_W_plaza_E_corridor'); mw=cor.matrix_world; inv=mw.inverted()
W=[mw@v.co for v in cor.data.vertices]
def eWy(y): return min(w.x for w in W if abs(w.y-y)<0.05) if any(abs(w.y-y)<0.05 for w in W) else None
xmin=min(w.x for w in W); xmax=max(w.x for w in W)
for v,w in zip(cor.data.vertices,W):
    x0=-218.55+(w.y+203.3)*((-220.05+0.30*(-192.3+192.3)+1.25)+218.55)/(-192.3+203.3)  # WS116 eW(y)
    xn=x0+(w.x-x0)*(XB+0.02-x0)/(xmax-x0) if w.x>x0+1e-4 else w.x
    w2=Vector((xn,w.y,w.z-0.05*(w.x-xn))); v.co=inv@w2
cor.data.update()
cor.name='WS116_Chapin_W_plaza_E_corridor_concrete_5pct_to_stair_foot_ws117'
Wn=[mw@v.co for v in cor.data.vertices]
foot=[w.z for w in Wn if abs(w.x-(XB+0.02))<0.03]
ZF=max(foot); r=(ZL-ZF)/N
print('M117 corridor foot z %.3f..%.3f rise %.3f riser %.4f'%(min(foot),ZF,ZL-ZF,r))
def box(bm,x0,x1,y0,y1,z0,z1):
    v=[bm.verts.new(c) for c in ((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([v[i] for i in f])
def link(name,bm,mat):
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-5)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
NEW=[]
# 2) stair: treads level, each block to below the foot
bm=bmesh.new()
for k in range(1,N):
    x0=XB+(k-1)*T; box(bm,x0,XT+0.01,YS,YC,ZF-0.35,ZF+k*r)
NEW.append(link('WS117_Chapin_W_entrance_stair_11R_concrete_LiDAR2023_UNVERIFIEDrisers',bm,mc))
# 3) landing + N terrace along the facade
bm=bmesh.new()
box(bm,XT,XW,YS,YC+CW,ZF-0.35,ZL)
ys=np.linspace(YC+CW,YN,9)
for a,b in zip(ys[:-1],ys[1:]):
    xe=max(xr(a),xr(b))-0.01
    box(bm,xe,XW,a,b+0.01,ZL-1.2,ZL)
NEW.append(link('WS117_Chapin_W_entrance_landing_terrace_concrete_LiDAR124.75_ortho2020_UNVERIFIEDext',bm,mc))
# 4) white walls: N stair cheek (sloped top in steps) + terrace edge wall on the bed side + N end return
bm=bmesh.new()
for k in range(N):
    x0=XB-0.3 if k==0 else XB+(k-1)*T; x1=XB+k*T if k<N-1 else XT+0.3
    box(bm,x0,x1,YC,YC+CW,ZF-0.35,min(ZF+k*r+0.55,ZL+0.45))
for a,b in zip(ys[:-1],ys[1:]):
    xe=min(xr(a),xr(b))-CW; zb_=min(dtm(xe,a),dtm(xe,b))-0.25
    box(bm,xe,xe+CW+0.01,a,b+0.01,zb_,ZL+0.45)
# (no N return wall: the terrace continues at entrance level into the ground N of y -182, LiDAR 124.6-124.8)
NEW.append(link('WS117_Chapin_W_entrance_cheek_and_terrace_edge_walls_white_UNVERIFIEDheight',bm,wallm))
# 5) handrails: S rail on the wing face side, N rail inside the cheek, 0.86 m over the nosings, posts ~1.2 m
bm=bmesh.new()
for yr in (YS+0.25,YC-0.12):
    A=(XB+0.15,ZF+r+0.86); B=(XT-0.15,ZF+(N-1)*r+0.86)
    npost=max(2,int((B[0]-A[0])/1.2)+1)
    for k in range(npost):
        t=k/(npost-1); xx=A[0]+t*(B[0]-A[0]); zz=A[1]+t*(B[1]-A[1]); kk=int(np.clip(np.floor((xx-XB)/T)+1,1,N-1))
        box(bm,xx-0.025,xx+0.025,yr-0.025,yr+0.025,ZF+kk*r,zz)
    # top rail + 0.3 m level extensions at both ends
    pts=[(A[0]-0.3,A[1]-r),(A[0],A[1]),(B[0],B[1]),(B[0]+0.3,B[1])]
    for (xa,za),(xb,zb) in zip(pts[:-1],pts[1:]):
        v=[bm.verts.new((xx,yr+dy,zz+dz)) for (xx,zz) in ((xa,za),(xb,zb)) for dy,dz in ((-0.02,-0.02),(0.02,-0.02),(0.02,0.02),(-0.02,0.02))]
        for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bm.faces.new([v[i] for i in f])
NEW.append(link('WS117_Chapin_W_entrance_stair_handrails_steel_UNVERIFIED',bm,steel))
# 5b) entrance: glazed double doors in the W face on the stair axis + flat canopy on two piers (LiDAR first returns 129.8-130.7 over x -212..-211, y -201..-198)
winm=O('WS108_Chapin_windows_grid').active_material
YM=0.5*(YS+YC); bm=bmesh.new()
box(bm,XW-0.12,XW+0.05,YM-1.25,YM+1.25,ZL,ZL+2.75)
NEW.append(link('WS117_Chapin_W_entrance_doors_glazed_UNVERIFIED',bm,winm))
bm=bmesh.new()
box(bm,XW-0.16,XW+0.05,YM-1.45,YM-1.25,ZL,ZL+2.95); box(bm,XW-0.16,XW+0.05,YM+1.25,YM+1.45,ZL,ZL+2.95); box(bm,XW-0.16,XW+0.05,YM-1.45,YM+1.45,ZL+2.75,ZL+2.95)
box(bm,XT+0.9,XW+0.05,YS+0.05,YC+0.2,130.05,130.40)
for yp in (YS+0.25,YC):
    box(bm,XT+0.9,XT+1.25,yp-0.0,yp+0.35 if yp==YC else yp+0.35,ZL,130.05)
NEW.append(link('WS117_Chapin_W_entrance_frame_canopy_piers_white_LiDARfirstreturn_UNVERIFIEDform',bm,wallm))
# 6a) stretch the E1/E2 beds' E edge from eE(y) to the wall at xr(y)-CW (ortho: bed runs to ~x -212.5 at y -190)
for pn in ('WS116_Chapin_W_bed_E1','WS116_Chapin_W_bed_E2'):
    o=O(pn); mw2=o.matrix_world; inv2=mw2.inverted(); me=o.data; ws=[mw2@v.co for v in me.vertices]
    rows={}
    for w in ws: rows.setdefault(round(w.y,3),[]).append(w.x)
    for v,w in zip(me.vertices,ws):
        xs=rows[round(w.y,3)]; xw=min(xs); xe=max(xs); xt=xr(w.y)-CW+0.02
        if xe-xw>1e-3 and xt>xe: w.x=xw+(w.x-xw)*(xt-xw)/(xe-xw); v.co=inv2@w
    me.update(); print('M117 stretch',o.name[:30])
# 6) regrade the WS116 E beds to the LiDAR slope up toward the terrace (they sat at forecourt grade, 1.2 m below it)
for pn in ('WS116_Chapin_W_bed_E1','WS116_Chapin_W_bed_E2'):
    o=O(pn); mw2=o.matrix_world; inv2=mw2.inverted(); me=o.data
    top={}; mx=0
    ws=[mw2@v.co for v in me.vertices]; zmax=max(w.z for w in ws)
    # top verts: grid verts (first (nu+1)*(nv+1)); skirt verts are 0.15 below a top vert at same xy
    keyz={}
    for w in ws:
        k=(round(w.x,3),round(w.y,3)); keyz[k]=max(keyz.get(k,-1e9),w.z)
    newz={}
    for k,z in keyz.items():
        zt=max(z,min(dtm(*k)-0.04,ZL-0.20)); newz[k]=zt; mx=max(mx,zt-z)
    for v,w in zip(me.vertices,ws):
        k=(round(w.x,3),round(w.y,3)); dz=w.z-keyz[k]; w.z=newz[k]+dz; v.co=inv2@w
    me.update(); print('M117 regrade',o.name[:30],'max lift %.2f'%mx)
for o in NEW: print('M117 new',o.name,'faces',len(o.data.polygons))
# 7) terrain: keep it under the stair / landing / terrace footprint
def inside(x,y):
    if YS<=y<=YC+CW and XB-0.05<=x<=XW: return ZF+max(1,min(N-1,int((x-XB)/T)+1))*r if x<XT else ZL
    if YC+CW<y<=YN+CW and xr(y)-CW<=x<=XW: return ZL+0.45 if x<xr(y) else ZL
    return None
for pn in ('WS113_terrain_fan_fill','WS110_ground_patch','Terrain_LiDAR_DTM_1m'):
    try: o=O(pn)
    except StopIteration: continue
    m2=o.data; mw2=o.matrix_world; inv2=mw2.inverted(); nd=0
    for v in m2.vertices:
        w=mw2@v.co
        if not (-218<w.x<-208.5 and -202<w.y<-184): continue
        zt=inside(w.x,w.y)
        if zt is not None and w.z>zt-0.06: w.z=zt-0.06; v.co=inv2@w; nd+=1
    m2.update(); print('M117 terrain',o.name[:30],'down',nd)
# 8) paving proxy: drop corridor faces past the foot, add stair/landing tops
pv=bpy.data.objects.get('WS113_paving_tops_proxy')
if pv:
    b2=bmesh.new(); b2.from_mesh(pv.data); n0=len(b2.faces); pmw=pv.matrix_world
    dl=[f for f in b2.faces if (lambda c:(XB<c.x<-212.0 and -200.6<c.y<-196.5))(pmw@f.calc_center_median())]
    bmesh.ops.delete(b2,geom=dl,context='FACES')
    for o in NEW[:2]:
        t=bmesh.new(); t.from_mesh(o.data); t.normal_update(); bmesh.ops.delete(t,geom=[f for f in t.faces if f.normal.z<0.5],context='FACES')
        m3=bpy.data.meshes.new('tmp'); t.to_mesh(m3); t.free(); b2.from_mesh(m3); bpy.data.meshes.remove(m3)
    b2.to_mesh(pv.data); b2.free(); pv.data.update(); print('M117 proxy',n0,'-',len(dl),'->',len(pv.data.polygons))
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M117 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M117 SAVED',SAVE)

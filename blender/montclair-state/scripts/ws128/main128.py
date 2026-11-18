# ws128: UNIFY #33 root cause = unmodelled Chapin S drive. 2020 ortho (asphalt tone = road, 162/165/145 vs lawn ~90) +
# 2023 LiDAR (class-2 ground: NO curb step x-245..-239 for y -244..-235; asphalt-low intensity; curb step 12-20 cm on the drive N edge)
# show a curbless driveway mouth off College Ave E at the WS112 brick crossing and an asphalt drive/lot running E along Chapin's S lawn.
# Builds: depressed College Ave E curb at the mouth, asphalt apron (curb back -> brick W edge, N end round the WS127 bed bullnose with a curb nose),
# first drive section E of the brick to x -218 (N curb on the LiDAR step line; S edge y -247.5 at the LiDAR island; E end = construction end).
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/ws128/'
A=np.vstack([np.load(D+'las_pts.npy'),np.load(D+'las_E.npy')]); G=A[A[:,3]==2][:,:3]
def lz(x,y,r=0.7):
    d2=(G[:,0]-x)**2+(G[:,1]-y)**2; m=d2<r*r
    if m.sum()<3: m=d2<(2*r)**2
    w=1/(d2[m]+0.04); return float((G[m,2]*w).sum()/w.sum())
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
def bnd_pts(o):
    me=o.data; mw=o.matrix_world; ec={}
    for p in me.polygons:
        if p.normal.z<0.5: continue
        for k in p.edge_keys: ec[k]=ec.get(k,0)+1
    vs=set(i for k,c in ec.items() if c==1 for i in k); return [mw@me.vertices[i].co for i in vs]
br=O('WS112_CollegeAve_S_E_walk_N_brick_link'); BP=bnd_pts(br)
cb=O('WS102_CollegeAve_S_curb_E')
# brick W/E edge polylines (min/max x per y band)
def edge(side,y0,y1):
    out=[]
    for v in sorted(BP,key=lambda v:-v.y):
        if y1<=v.y<=y0: out.append(v)
    rows={}
    for v in out: rows.setdefault(round(v.y*2.1),[]).append(v)
    pts=[(min(r,key=lambda v:v.x) if side=='W' else max(r,key=lambda v:v.x)) for k,r in sorted(rows.items(),reverse=True)]
    return pts
BW=[v for v in edge('W',-234.85,-245.2)]
BE=[v for v in edge('E',-238.3,-246.1) if v.x<-234.3]
print('M128 brick W',len(BW),BW[0][:],BW[-1][:],' E',len(BE),BE[0][:],BE[-1][:])
# curb back-top edge
cv=[cb.matrix_world@v.co for v in cb.data.vertices]
_cb=[]
for yy in np.arange(-244.1,-231.0,0.4):
    s_=[v for v in cv if abs(v.y-yy)<0.26]
    if s_:
        top=max(v.z for v in s_); b=max((v for v in s_ if v.z>top-0.03),key=lambda v:v.x); _cb.append((b.y,b.x,b.z))
_cb=np.array(_cb); CBX=np.polyfit(_cb[:,0],_cb[:,1],1); CBZ=np.polyfit(_cb[:,0],_cb[:,2],1)
def curb_back(y): return Vector((float(np.polyval(CBX,y)),y,float(np.polyval(CBZ,y))))
# resample helper
def resamp(pl,n):
    L=[0]
    for a,b in zip(pl,pl[1:]): L.append(L[-1]+(b.xy-a.xy).length)
    out=[]
    for i in range(n+1):
        t=L[-1]*i/n; k=max(j for j in range(len(L)) if L[j]<=t+1e-9); k=min(k,len(pl)-2)
        f=(t-L[k])/max(L[k+1]-L[k],1e-9); out.append(pl[k].lerp(pl[k+1],f))
    return out
def coons(N,S,W,E):
    # N,S: lists len nu+1 (W->E); W,E: len nv+1 (N->S)
    nu=len(N)-1; nv=len(W)-1; P=[]
    for j in range(nv+1):
        v=j/nv; row=[]
        for i in range(nu+1):
            u=i/nu
            p=(1-v)*N[i].xy+v*S[i].xy+(1-u)*W[j].xy+u*E[j].xy-((1-u)*(1-v)*N[0].xy+u*(1-v)*N[-1].xy+(1-u)*v*S[0].xy+u*v*S[-1].xy)
            row.append(p)
        P.append(row)
    return P
bm=bmesh.new(); topf=[]
def grid_mesh(P,zf):
    vv=[[bm.verts.new((p.x,p.y,zf(p.x,p.y))) for p in row] for row in P]
    for j in range(len(vv)-1):
        for i in range(len(vv[0])-1):
            f=bm.faces.new((vv[j][i],vv[j+1][i],vv[j+1][i+1],vv[j][i+1])); topf.append(f)
    return vv
# ---- W apron (driveway mouth)
yN=-232.75
cx=-237.2; R=1.42; YS=-232.6
bed=bpy.data.objects.get('WS127_CollegeAve_E_curbside_bed_mulch_ortho2020_UNVERIFIED')
if bed:
    bv=[bed.matrix_world@v.co for v in bed.data.vertices]; low=min(bv,key=lambda v:v.y); cx=low.x
    xs=[v.x for v in bv if abs(v.y-YS)<0.3]; R=(max(xs)-min(xs))/2; cx=(max(xs)+min(xs))/2
    print('M128 bullnose cx',round(cx,3),'R',round(R,3),'low',round(low.y,3))
RN=R+0.16  # asphalt meets the outer face of a 0.16 m curb nose round the bed end
arc=[Vector((cx+RN*math.cos(math.radians(a)),YS+RN*math.sin(math.radians(a)),0)) for a in range(180,301,8)]
cbn=curb_back(-232.9)
Nl=[Vector((cbn.x,cbn.y,0))]+[a for a in arc if a.x>cbn.x+0.05]+[BW[0]]
Wl=[Vector((curb_back(y).x,y,0)) for y in np.linspace(cbn.y,-244.45,24)]
Sl=[Wl[-1],BW[-1]]
nu=16; nv=24
Nr=resamp(Nl,nu); Sr=resamp(Sl,nu); Wr=resamp(Wl,nv); Er=resamp(BW,nv)
Er[0]=Nr[-1]; Wr[0]=Nr[0]; Wr[-1]=Sr[0]; Er[-1]=Sr[-1]
PW=coons(Nr,Sr,Wr,Er)
# heights: LiDAR, then pinned to brick edge (flush, -5 mm) and curb (flush) by distance blend
Bt=[v for v in BW]
def zW(x,y):
    z=lz(x,y)
    d=min((Vector((x,y))-b.xy).length for b in Bt)
    if d<0.8:
        b=min(Bt,key=lambda b:(Vector((x,y))-b.xy).length); t=d/0.8; z=(1-t)*(b.z-0.005)+t*z
    return z
vW=grid_mesh(PW,zW)
# ---- E drive section
def yNc(x): return -239.0-0.233*(x+232.0)   # LiDAR curb-step fit (x -232..-208)
XE=-218.0
# NW corner: where the curb line meets the brick E edge
nw=min(BE,key=lambda b:abs(b.y-yNc(b.x)))
BE2=[b for b in BE if b.y<=nw.y+1e-6]
NE=[Vector((x,yNc(x),0)) for x in np.linspace(nw.x,XE,20)]
NE[0]=nw
SE=[BE2[-1],Vector((XE,-247.5,0))]
nu2=28; nv2=12
Nr2=resamp(NE,nu2); Sr2=resamp(SE,nu2); Wr2=resamp(BE2,nv2); Er2=resamp([NE[-1],SE[-1]],nv2)
Nr2[0]=Wr2[0]; Nr2[-1]=Er2[0]; Sr2[0]=Wr2[-1]; Sr2[-1]=Er2[-1]
PE=coons(Nr2,Sr2,Wr2,Er2)
Bt2=BE2
def zE(x,y):
    z=lz(x,y)
    # LiDAR right at the N edge mixes curb-top points: sample 0.5 m into the drive
    if y>yNc(x)-0.6: z=lz(x,yNc(x)-0.6)+(lz(x,yNc(x)-0.6)-lz(x,yNc(x)-1.2))*0.0
    d=min((Vector((x,y))-b.xy).length for b in Bt2)
    if d<0.8:
        b=min(Bt2,key=lambda b:(Vector((x,y))-b.xy).length); t=d/0.8; z=(1-t)*(b.z-0.005)+t*z
    return z
vE=grid_mesh(PE,zE)
# light smoothing of interior z (LiDAR noise), boundaries pinned
for vv in (vW,vE):
    for it in range(3):
        nz={}
        for j in range(1,len(vv)-1):
            for i in range(1,len(vv[0])-1):
                nz[(j,i)]=(vv[j-1][i].co.z+vv[j+1][i].co.z+vv[j][i-1].co.z+vv[j][i+1].co.z)/4*0.6+vv[j][i].co.z*0.4
        for (j,i),z in nz.items(): vv[j][i].co.z=z
bm.normal_update()
for f in topf:
    if f.normal.z<0: f.normal_flip()
# skirts on boundary edges (8 cm, asphalt) so no light slot at the lawn
for e in [e for e in bm.edges if e.is_boundary]:
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0005)
me=bpy.data.meshes.new('WS128_drive_asphalt'); bm.to_mesh(me); bm.free()
# asphalt material = whatever College Ave S road uses
road=None
for o in bpy.data.objects:
    if o.type=='MESH' and any(m and 'sphalt' in m.name for m in o.data.materials):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(v.x for v in bb)<-244<max(v.x for v in bb) and min(v.y for v in bb)<-238<max(v.y for v in bb) and 'WS128' not in o.name: road=o; break
am=next(m for m in road.data.materials if m and 'sphalt' in m.name) if road else bpy.data.materials.get('Asphalt')
am=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho') or am
print('M128 road obj',road.name if road else None,'mat',am.name)
me.materials.append(am)
col=bpy.data.collections.get('WS128_Chapin_S_drive') or bpy.data.collections.new('WS128_Chapin_S_drive')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS128_')]: bpy.data.objects.remove(o)
dr=bpy.data.objects.new('WS128_Chapin_S_drive_mouth_and_drive_asphalt_LiDAR2023_ortho2020_UNVERIFIEDextent',me); col.objects.link(dr)
# ---- curbs: drive N curb (0.15 m wide, 0.14 m reveal) + curb nose round the bed end
cm=cb.active_material
def curb_strip(name,pl,zf,w=0.15,rev=0.14,side=1):
    bm=bmesh.new(); prev=None
    for k,p in enumerate(pl):
        a=pl[min(k+1,len(pl)-1)]-pl[max(k-1,0)]; t=a.xy.normalized(); n=Vector((-t.y,t.x))*side
        z=zf(p.x,p.y); q=p.xy; q2=q+n*w
        ring=[bm.verts.new((q.x,q.y,z-0.2)),bm.verts.new((q.x,q.y,z+rev)),bm.verts.new((q2.x,q2.y,z+rev)),bm.verts.new((q2.x,q2.y,z-0.2))]
        if prev:
            for i in range(3): bm.faces.new((prev[i],ring[i],ring[i+1],prev[i+1]))
        prev=ring
    me=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(cm)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
NEc=[Vector((x,yNc(x),0)) for x in np.linspace(nw.x+0.1,XE,40)]
c1=curb_strip('WS128_Chapin_S_drive_N_curb_LiDAR_step_UNVERIFIED',NEc,lambda x,y:zE(x,y-0.01),side=1)
arcc=[Vector((cx+RN*math.cos(math.radians(a)),YS+RN*math.sin(math.radians(a)),0)) for a in range(186,355,6)]
arcc=[a for a in arcc if a.x>cbn.x+0.1]
c2=curb_strip('WS128_CollegeAve_E_bed_end_curb_nose_UNVERIFIED',arcc,lambda x,y:zW(x,y),w=0.16,rev=0.10,side=-1)
# ---- depressed College Ave E curb across the mouth (LiDAR: no step y -244..-235)
nd=0
for cobj in [o for o in bpy.data.objects if o.name.startswith(('WS102_CollegeAve_S_curb_E','WS111_CollegeAve_S_curb_E_bridge'))]:
    mw=cobj.matrix_world; mi=mw.inverted()
    for v in cobj.data.vertices:
        p=mw@v.co
        if not (-245.0<p.y<-233.5): continue
        y=p.y
        f=1.0 if -243.9<=y<=-234.6 else (max(0,(y+245.0)/1.1) if y<-243.9 else max(0,(-233.5-y)/1.1))
        tz=lz(p.x,p.y)+0.015
        if p.z>tz:
            p.z=p.z-f*(p.z-tz); v.co=mi@p; nd+=1
print('M128 curb verts depressed',nd)
# ---- ground under the new paving
def inpoly(poly,x,y):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: c=not c
    return c
polyW=[(p.x,p.y) for p in Nr]+[(p.x,p.y) for p in Er[1:]]+[(p.x,p.y) for p in reversed(Sr[:-1])]+[(p.x,p.y) for p in reversed(Wr[1:-1])]
polyE=[(p.x,p.y) for p in Nr2]+[(p.x,p.y) for p in Er2[1:]]+[(p.x,p.y) for p in reversed(Sr2[:-1])]+[(p.x,p.y) for p in reversed(Wr2[1:-1])]
from mathutils.bvhtree import BVHTree
tree=BVHTree.FromPolygons([v.co for v in me.vertices],[p.vertices for p in me.polygons if p.normal.z>0.5])
nl=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (-244<p.x<-216 and -249<p.y<-232): continue
        hit=False
        for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            if inpoly(polyW,p.x+dx,p.y+dy) or inpoly(polyE,p.x+dx,p.y+dy): hit=True; break
        if not hit: continue
        loc=tree.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))[0]
        zb=loc.z if loc is not None else lz(p.x,p.y)
        if p.z>zb-0.12: p.z=zb-0.12; v.co=mi@p; nl+=1
print('M128 ground verts lowered',nl)
# lawn S of the drive S edge / E construction end: lift ground verts within 1 m to meet the slab edge (no slot)
nr=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (-239<p.x<-216 and -249.5<p.y<-239): continue
        if inpoly(polyE,p.x,p.y): continue
        ys=-247.5+(-246.03+247.5)*(XE-p.x)/(XE-Sr2[0].x) if p.x>Sr2[0].x else None
        d=None
        if ys is not None and p.y<ys and ys-p.y<1.0: d=ys-p.y; ze=zE(p.x,ys)-0.01
        elif p.x>XE and p.x-XE<1.0 and yNc(XE)>p.y>-247.5: d=p.x-XE; ze=zE(XE,p.y)-0.01
        if d is None: continue
        t=d/1.0; zt=ze*(1-t)+p.z*t
        if abs(zt-p.z)>0.005: p.z=zt; v.co=mi@p; nr+=1
print('M128 edge lawn verts graded',nr)
# proxy: so the WS113 edge-grade GN keeps lawn at/under the new paving and lifts lawn to the N curb top
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws128'):
    px['ws128']=1
    pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in (dr,c1,c2):
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M128 proxy faces',n0,'->',len(px.data.polygons))
print('M128 drive faces',len(me.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('M128 SAVED')

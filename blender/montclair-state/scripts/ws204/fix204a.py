# ws204 W22 (College Ave crosswalk by the Red Hawk deck SE core): plan probe p204_w22.json shows a ~14 x 9 m HOLE in the paving,
# x -263.3..-249.6, y -57.2..-66 — there only the green-tinted WS68 ground drape shows (the 'lawn' in the survey render), bounded by
# KY carriageway's stair-stepped S edge (the jagged diagonal). NJ 2020 ortho (ortho_w22z_grid.png, 0.025 m/px resample) shows this is
# continuous asphalt: the College Ave / accessible-lot entrance throat, carrying (a) the N-S ladder crossing continuing from the
# ey ladder (y -58.6) to the WS76 zebra (y -65) and (b) an E-W zebra across the lot entrance, x -259.2..-251.6, y -61.9..-65.5.
# Designer call: one asphalt sheet on a smooth quadratic grade fitted to the surrounding paving (KY/WS74/WS76), tucked 4 mm under every
# existing paved/grass surface so no existing edge moves; KY carriageway material so KY's stepped edge disappears into the same asphalt.
# Paint: ladder bars at 1 m pitch (matching ey/WS76 bars) + E-W zebra 8 bars (count/width from the ortho, UNVERIFIED +-0.1 m). Stop bar
# at (-256..-252.5,-61) in the ortho NOT modelled (type unclear).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    me=o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh(); mw=o.matrix_world
    t=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); return t
def ob(pfx): return [o for o in bpy.data.objects if o.name.startswith(pfx)][0]
KY=ob('KY_college_ave_carriageway_asphalt'); W74=ob('WS74_cogen_lot_asphalt'); W76=ob('WS76_accessible_lot_asphalt'); G68=ob('WS68_RHD_ground_northDTM')
OTH=[ob(p) for p in ['KY_college_ave_carriageway_asphalt','WS74_cogen_lot_asphalt','WS76_accessible_lot_asphalt','WS70_gap_strip_grass_berms','WS67_CollegeAve_gap_asphalt','ey_rhd_se_crosswalks','WS76_lot_zebra_walkway_paint','WS76_lot_stall_paint_white','WS69_CollegeAve_gap_strip_curbs','KX_drive_apron','LH_college_ave_gutter_asphalt_fill']]
T={o.name:bvh(o) for o in OTH}; T68=bvh(G68)
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,140)),Vector((0,0,-1)),40)
    return h[0].z if h[0] is not None else None
# fit samples: paving ring
SMP=[]
for x in np.arange(-266,-249,0.5):
    for y in np.arange(-68,-55,0.5):
        for o in (KY,W74,W76):
            z=hz(T[o.name],x,y)
            if z is not None and hz(T[OTH[3].name],x,y) is None: SMP.append((x,y,z)); break
SMP=np.array(SMP); X=SMP[:,0]+257; Y=SMP[:,1]+61
A=np.c_[np.ones_like(X),X,Y,X*X,X*Y,Y*Y]; c,*_=np.linalg.lstsq(A,SMP[:,2],rcond=None)
res=SMP[:,2]-A@c; print('F204a fit n',len(S),'rms %.4f max %.4f'%(np.sqrt((res**2).mean()),abs(res).max()),flush=True)
def fit(x,y):
    b=float(np.dot(c,[1,x+257,y+61,(x+257)**2,(x+257)*(y+61),(y+61)**2]))
    d2=(SMP[:,0]-x)**2+(SMP[:,1]-y)**2; w=1.0/(d2+0.05)**2; return b+float((w*res).sum()/w.sum())
# polygon: W x=-263.3, N y=-57.2 to berm tip, berm SW edge (diagonal) to (-249.6,-61.2), E x=-249.6, S y=-66.8
POLY=[(-263.3,-57.2),(-256.5,-57.2),(-249.6,-61.2),(-249.6,-66.8),(-263.3,-66.8)]
def inside(x,y,P=POLY):
    c=False; n=len(P)
    for k in range(n):
        (x1,y1),(x2,y2)=P[k],P[(k+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
st=0.25
xs=np.arange(-263.3,-249.6+1e-6,st); ys=np.arange(-66.8,-57.2+1e-6,st)
bm=bmesh.new(); V={}
for i,x in enumerate(xs):
    for j,y in enumerate(ys):
        z=fit(x,y); g=hz(T68,x,y)
        if g is not None: z=max(z,g+0.006)
        for n,t in T.items():
            zo=hz(t,x,y)
            if zo is not None and zo<z+0.004: z=zo-0.004
        V[(i,j)]=bm.verts.new((x,y,z))
nf=0
for i in range(len(xs)-1):
    for j in range(len(ys)-1):
        cx=(xs[i]+xs[i+1])/2; cy=(ys[j]+ys[j+1])/2
        if inside(cx,cy):
            bm.faces.new([V[(i,j)],V[(i+1,j)],V[(i+1,j+1)],V[(i,j+1)]]); nf+=1
for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
# cut the fill exactly along the (straight) WS70 berm W-end / SW / E-end base edges, 3 cm under the berm, drop faces inside it
BW=[(-255.533,-56.417),(-256.493,-58.172)]; BS=[(-256.493,-58.172),(-250.408,-61.501)]; BE=[(-250.408,-61.501),(-249.448,-59.747)]
FOOT=[(-255.533,-56.417),(-256.493,-58.172),(-250.408,-61.501),(-249.448,-59.747),(-249.0,-55.0),(-255.0,-55.2)]
cen=np.mean(FOOT[:4],axis=0)
def off(p,q,d=0.03):
    p=np.array(p);q=np.array(q); t=q-p; n=np.array((-t[1],t[0]))/np.linalg.norm(t)
    if np.dot(cen-p,n)<0: n=-n
    return p+n*d,n
for L in (BW,BS,BE):
    p0,n=off(*L)
    bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],dist=0.002,plane_co=(p0[0],p0[1],0),plane_no=(n[0],n[1],0))
def dline(x,y):
    best=9
    for L in (BW,BS,BE):
        p0,n=off(*L); a=np.array(L[0]); b=np.array(L[1]); t=np.clip(np.dot((np.array((x,y))-a),(b-a))/np.dot(b-a,b-a),0,1)
        if t<=0 or t>=1: continue
        best=min(best,abs(np.dot(np.array((x,y))-p0,n)))
    return best
FOOTS=[]
for k,p in enumerate(FOOT): FOOTS.append(p)
dead=[f for f in bm.faces if inside(*tuple(f.calc_center_median())[:2],P=FOOT) and dline(*tuple(f.calc_center_median())[:2])>0.0 and not (dline(*tuple(f.calc_center_median())[:2])<0.0)]
dead=[f for f in dead if all(inside(v.co.x,v.co.y,P=FOOT) or dline(v.co.x,v.co.y)<0.005 for v in f.verts)]
bmesh.ops.delete(bm,geom=dead,context='FACES')
T70=T[OTH[3].name]; nl=0
for v in bm.verts:
    x,y=v.co.x,v.co.y
    zz=fit(x,y); g=hz(T68,x,y)
    if g is not None: zz=max(zz,g+0.006)
    for n_,t in T.items():
        zo=hz(t,x,y)
        if zo is not None and zo<zz+0.004: zz=zo-0.004
    if dline(x,y)<0.01:
        zb=None
        for L in (BW,BS,BE):
            p0,n=off(*L); q=np.array((x,y))+n*0.05; zb=hz(T70,q[0],q[1]) or zb
        if zb is not None: zz=min(zz,zb-0.005); nl+=1
    v.co.z=zz
print('F204a berm cut: dead',len(dead),'line verts',nl,flush=True)
me=bpy.data.meshes.new('WS204_fill'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
NM='WS204_CollegeAve_lot_entrance_asphalt_fill_ortho2020'
o=bpy.data.objects.new(NM,me); KY.users_collection[0].objects.link(o); me.materials.append(KY.data.materials[0])
print('F204a fill faces',nf,'mat',KY.data.materials[0].name,flush=True)
# paint
PM=ob('ey_rhd_se_crosswalks').data.materials[0]
def bar(bm,corners):
    vs=[]
    for (x,y) in corners:
        z=hz(T68,x,y); zf=None
        # top surface under the bar: fill (fit) or existing paving
        cand=[hz(t,x,y) for t in T.values()]; cand=[q for q in cand if q is not None]
        zz=fit(x,y); g=hz(T68,x,y)
        if g is not None: zz=max(zz,g+0.006)
        for q in cand:
            if q<zz+0.004: zz=q-0.004
        vs.append(bm.verts.new((x,y,zz+0.007)))
    bm.faces.new(vs)
bm=bmesh.new(); nb=0
# ladder bars y -59.1..-64.1, edges interpolated (-260.5,-258.4)@-58.1 -> (-261.8,-259.7)@-65.1
for k in range(1,7):
    dx=-0.3*k; dy=-1.08*k; xl=-260.92+dx; xr=-257.59+dx
    yl=-57.865+dy-0.224*(xl-dx+260.46); yr=-57.865+dy-0.224*(xr-dx+260.46)
    bar(bm,[(xl,yl-0.25),(xr,yr-0.25),(xr,yr+0.25),(xl,yl+0.25)]); nb+=1
# E-W zebra: block NW(-259.2,-61.9) NE(-251.6,-62.7) SE(-251.6,-65.5) SW(-259.2,-64.7); 8 bars 0.5 m wide, pitch 0.95 m
for k in range(8):
    xa=-258.55+k*0.9; xb=xa+0.5
    yt=lambda x:-61.9+(x+259.2)*(-0.8/7.6); yb=lambda x:-64.7+(x+259.2)*(-0.8/7.6)
    bar(bm,[(xa,yb(xa)),(xb,yb(xb)),(xb,yt(xb)),(xa,yt(xa))]); nb+=1
me2=bpy.data.meshes.new('WS204_paint'); bm.to_mesh(me2); bm.free()
for p in me2.polygons:
    if p.normal.z<0: p.flip()
o2=bpy.data.objects.new('WS204_lot_entrance_crosswalk_paint_ortho2020_UNVERIFIED_bars',me2); KY.users_collection[0].objects.link(o2); me2.materials.append(PM)
print('F204a paint bars',nb,'mat',PM.name,flush=True)
# stray WS76 lot-zebra bars that overlap the ey ladder at y -55.5..-57 (the doubled 4th/5th bar in the survey render)
Z=ob('WS76_lot_zebra_walkway_paint'); mz=Z.matrix_world; bz=bmesh.new(); bz.from_mesh(Z.data); kill=[]
for f in bz.faces:
    ps=[mz@v.co for v in f.verts]
    if all(-261.5<p.x<-256.5 and -57.8<p.y<-54.5 for p in ps): kill.append(f); print('F204a stray WS76 zebra face',[ (round(p.x,2),round(p.y,2)) for p in ps],flush=True)
bmesh.ops.delete(bz,geom=kill,context='FACES'); bz.to_mesh(Z.data); bz.free(); Z.data.update(); print('F204a stray removed',len(kill),flush=True)

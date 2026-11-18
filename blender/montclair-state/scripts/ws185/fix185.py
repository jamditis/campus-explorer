# ws185 — PLAN day 20 task 6: Lot 36 N edge vs the Sprague Field turf-edge curb. DRAFT — NOT YET SUBSET-TESTED (written while the weekly
# perf routine held .lock); do NOT add to a merge chain until a subset run (sub182.py FIXES="... ws185/fix185.py" NORENDER=1) prints sane FIX185 lines.
# Evidence: prep/ws185_lot36N/NOTES.md (2020 NJOGIS ortho curb picks -> circle c=(-342.26,-179.12) R=44.00; 2023 class-2 intensity edges).
# (a) clamp WS181 lot verts that sit N of the curb (inside the turf) back to 0.10 m S of it; (b) concrete curb ribbon 0.2 m along arc + E straight;
# (c) worn-grass sheet between the lot N edge and the curb, x -352..-328, under paving. Curb height/profile UNVERIFIED (LiDAR step < 5 cm).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
CX,CY,R=-342.26,-179.12,44.00
E0,E1=Vector((-317.6,-214.2)),Vector((-315.7,-200.0))     # E-side straight curb (ortho by eye, +-0.3 m)
DZ=np.load('/workspace/nj-scenes/montclair-state/prep/ws185_lot36N/dtm185_0p25m.npy'); X0,Y1,RS=-352.,-190.,0.25
def dtm(x,y):
    fx=min(max((x-X0)/RS,0),DZ.shape[1]-1.001); fy=min(max((Y1-y)/RS,0),DZ.shape[0]-1.001); j,i=int(fx),int(fy); a,b=fy-i,fx-j
    q=DZ[i:i+2,j:j+2]; q=np.where(np.isnan(q),np.nanmean(q) if not np.all(np.isnan(q)) else 115.75,q)
    return float(q[0,0]*(1-a)*(1-b)+q[0,1]*(1-a)*b+q[1,0]*a*(1-b)+q[1,1]*a*b)
def curb_pts(step=0.25):
    # arc x -352..-320, then a quadratic Bezier fillet (control = arc tangent x E straight) into the E straight from y -212.7 to -200
    P=[]; x=-352.0
    while x<=-320.0+1e-9:
        P.append(Vector((x,CY-math.sqrt(R*R-(x-CX)**2)))); x+=step
    A=P[-1]; tA=Vector((1.0,(A.x-CX)/math.sqrt(R*R-(A.x-CX)**2))).normalized()
    d=(E1-E0).normalized(); B=E0+d*1.5
    # intersection of A+s*tA and B+u*d
    den=tA.x*d.y-tA.y*d.x; s_=((B.x-A.x)*d.y-(B.y-A.y)*d.x)/den; C=A+tA*s_
    for t in np.linspace(0,1,13)[1:]: P.append(A*(1-t)**2+C*2*(1-t)*t+B*t*t)
    L=(E1-B).length; n=int(L/step)
    for k in range(1,n+1): P.append(B.lerp(E1,k/n))
    return P
CP=curb_pts()
# (a) lot N boundary onto the curb: boundary verts N of the curb, or <=1.0 m S of it at x -329..-316 (evidence: asphalt meets the curb),
#     snap to 0.10 m S/E of the curb line; interior verts closer than 0.35 m get pushed to 0.35 m (keeps faces from collapsing).
def curb_foot(x,y):
    """nearest point on the curb polyline (arc + fillet + E straight) and signed offset (+ = lot side)."""
    best=None
    for p,q in zip(CP,CP[1:]):
        d=q-p; L2=d.length_squared; t=max(0.0,min(1.0,(Vector((x,y))-p).dot(d)/L2)); f=p+d*t; dd=(Vector((x,y))-f).length
        if best is None or dd<best[0]:
            n=Vector((d.y,-d.x)).normalized()   # right of W->E->N travel = lot side (S of the arc, E of the straight)
            best=(dd,f,n,(Vector((x,y))-f).dot(n))
    return best[1],best[2],best[3]
LOT=next((o for o in bpy.data.objects if o.name.startswith('WS181_Lot36_asphalt')),None)   # ws186: names are cut at 63 chars
if LOT is None: print('FIX185 SKIPPED lot missing',flush=True)
else:
    mw=LOT.matrix_world; inv=mw.inverted(); bm=bmesh.new(); bm.from_mesh(LOT.data); nb=ni=0; mx=0.0
    for v in bm.verts:
        w=mw@v.co
        if not (-352<w.x<-315 and -226<w.y<-198): continue
        f,n,off=curb_foot(w.x,w.y)
        bnd=v.is_boundary
        tgt=None
        if bnd and (off<0.10 or (off<1.0 and -329<w.x<-316)): tgt=0.10
        elif (not bnd) and off<0.35: tgt=0.35
        if tgt is not None:
            q=f+n*tgt; mx=max(mx,(Vector((w.x,w.y))-q).length); w.x,w.y=q.x,q.y; v.co=inv@w
            if bnd: nb+=1
            else: ni+=1
    bmesh.ops.dissolve_degenerate(bm,dist=0.02,edges=bm.edges[:])
    bm.to_mesh(LOT.data); bm.free(); LOT.data.update()
    print('FIX185 lot verts onto curb boundary %d interior %d max shift %.2f'%(nb,ni,mx),flush=True)
# (b) curb ribbon (0.20 m wide, top = DTM+0.05, 0.25 m deep)
NAME='WS185_Sprague_turf_edge_curb_ortho2020_UNVERIFIEDheight'
o=bpy.data.objects.get(NAME)
if o: bpy.data.objects.remove(o,do_unlink=True)
bm=bmesh.new(); rows=[]
for i,p in enumerate(CP):
    a=CP[max(i-1,0)]; b=CP[min(i+1,len(CP)-1)]; t=(b-a).normalized(); n=Vector((-t.y,t.x))   # n = left of travel (W->E travel: n points N/turf)
    z=dtm(p.x,p.y)
    q=[p-n*0.10,p+n*0.10]
    rows.append([bm.verts.new((q[0].x,q[0].y,z+0.05)),bm.verts.new((q[1].x,q[1].y,z+0.05)),
                 bm.verts.new((q[1].x,q[1].y,z-0.20)),bm.verts.new((q[0].x,q[0].y,z-0.20))])
for r0,r1 in zip(rows,rows[1:]):
    for k in range(4): bm.faces.new((r0[k],r0[(k+1)%4],r1[(k+1)%4],r1[k]))
bm.faces.new(rows[0][::-1]); bm.faces.new(rows[-1])
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new(NAME,me); bpy.context.scene.collection.objects.link(ob)
m=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
if m: me.materials.append(m)
print('FIX185 curb verts %d len %.1f m mat %s'%(len(me.vertices),sum((b-a).length for a,b in zip(CP,CP[1:])),m.name if m else None),flush=True)
# (c) worn-grass sheet between lot N edge and curb (x -352..-328): S boundary = lot edge evidence polyline pushed 0.3 m under the lot
NAME='WS185_Lot36_N_grass_strip_LiDAR2023int_UNVERIFIEDmown'
o=bpy.data.objects.get(NAME)
if o: bpy.data.objects.remove(o,do_unlink=True)
def lot_edge(x):
    if x<=-336: return -0.2848*x-327.58
    if x<=-333: return np.interp(x,[-336,-335,-334,-333],[-231.9,-227.8,-225.0,-223.5])
    return -223.6
bm=bmesh.new(); cols=[]
xs=np.arange(-352,-328.0+1e-6,0.5)
for x in xs:
    yc=CY-math.sqrt(R*R-(x-CX)**2); ye=lot_edge(x)-0.30; col=[]
    for t in np.linspace(0,1,6):
        y=ye+(yc-0.05-ye)*t; col.append(bm.verts.new((x,y,dtm(x,y)+(0.0 if 0<t<1 else -0.02))))
    cols.append(col)
for c0,c1 in zip(cols,cols[1:]):
    for k in range(5): bm.faces.new((c0[k],c1[k],c1[k+1],c0[k+1]))
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new(NAME,me); bpy.context.scene.collection.objects.link(ob)
m=bpy.data.materials.get('COLE_lawn_post2020_bs_nostripe_WS175') or bpy.data.materials.get('COLE_lawn_post2020_bs')
if m: me.materials.append(m)
print('FIX185 grass strip faces %d mat %s'%(len(me.polygons),m.name if m else None),flush=True)

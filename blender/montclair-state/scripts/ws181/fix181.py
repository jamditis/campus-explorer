# ws181 — PLAN day 20 task 5 (first pass): Lot 36 asphalt body + NE drive to the Sprague E service lane + W drive leaving the model edge.
# Evidence: prep/ws181_lot36/REFS.md (2023 LiDAR class-2 intensity 1 m map prep/ws180_lot36/asphalt_mask180.txt + las181_W.npy W of x -345;
# NJOGIS 2020 ortho ortho181_grid.png: uniform grey, NO stall paint; DTM flat ~115.7 = Sprague-field level, bank toe to Lot 3 at x -316..-313).
# ADDITIVE: one new mesh draped on the existing ground (top ray hit) + feathered 0.5->3 cm so it laps existing asphalt without a lip and
# covers the lawn it replaces. Edges UNVERIFIED (+-0.5-1 m), surface asphalt vs millings UNVERIFIED.
import bpy, bmesh, math, re
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt
NAME='WS181_Lot36_asphalt_LiDAR2023int_ortho2020_nostalls_UNVERIFIEDedges'
old=bpy.data.objects.get(NAME)
if old: bpy.data.objects.remove(old,do_unlink=True)
P=[(-317.8,-211.5),(-313.6,-211.5),(-314.2,-217.0),(-315.0,-223.0),(-316.0,-229.0),(-317.2,-234.5),(-319.0,-238.0),(-322.0,-238.6),
   (-328.0,-238.8),(-334.0,-238.6),(-338.0,-238.4),(-345.0,-237.4),(-351.0,-235.0),(-356.2,-232.4),(-356.2,-226.0),(-350.0,-228.6),
   (-345.0,-230.2),(-338.5,-230.0),(-335.5,-228.5),(-334.2,-225.5),(-332.0,-223.6),(-328.0,-221.6),(-324.0,-219.3),(-320.8,-216.5),(-318.8,-213.5)]
KEEP={1,13,14}   # sharp corners kept (NE drive end at the service lane, W drive end at the model edge)
def chaikin(pts,it=2):
    for _ in range(it):
        q=[]; n=len(pts)
        for i in range(n):
            a=pts[i]; b=pts[(i+1)%n]
            if i in KEEP: q.append(a)
            else: q.append((0.75*a[0]+0.25*b[0],0.75*a[1]+0.25*b[1]))
            if (i+1)%n in KEEP: q.append(((a[0]+b[0])/2,(a[1]+b[1])/2))
            else: q.append((0.25*a[0]+0.75*b[0],0.25*a[1]+0.75*b[1]))
        # re-index corners
        newkeep=set(); j=0
        for i in range(n):
            if i in KEEP: newkeep.add(j)
            j+=2
        pts=q; KEEP.clear(); KEEP.update(newkeep)
    return pts
B=chaikin(P,2)
# resample boundary every <=0.5 m
R=[]
for i in range(len(B)):
    a=Vector(B[i]); b=Vector(B[(i+1)%len(B)]); L=(b-a).length; k=max(1,int(math.ceil(L/0.5)))
    for j in range(k): R.append(a.lerp(b,j/k))
def inside(x,y,poly):
    c=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
def dist_b(x,y):
    best=1e9
    for i in range(len(R)):
        a=R[i]; b=R[(i+1)%len(R)]; ab=b-a; t=max(0,min(1,((Vector((x,y))-a).dot(ab))/max(ab.length_squared,1e-9)))
        best=min(best,(a+ab*t-Vector((x,y))).length)
    return best
Bp=[(v.x,v.y) for v in R]
xs=[p[0] for p in Bp]; ys=[p[1] for p in Bp]
pts=[Vector((v.x,v.y)) for v in R]; nb=len(pts)
x=math.floor(min(xs)); 
while x<=max(xs):
    y=math.floor(min(ys))
    while y<=max(ys):
        if inside(x,y,Bp) and dist_b(x,y)>0.25: pts.append(Vector((x,y)))
        y+=0.5
    x+=0.5
res=delaunay_2d_cdt(pts,[(i,(i+1)%nb) for i in range(nb)],[list(range(nb))],1,1e-5)
V2,E2,F2=res[0],res[1],res[2]
# ground objects to drape on (top hit), resolved by name in the open file
GRX=re.compile(r'^(WS167_ground|WS167_Sprague_E_service|WS169c|WS163_ground_patch|WS162_Lot3_W_shoulder|WS163_Lot3_aisle_S_drive|WS162_Lot3_S_end_apron)')
GO=[o for o in bpy.data.objects if o.type=='MESH' and GRX.match(o.name) and 'hidden' not in o.name and 'skirt_target' not in o.name]
print('FIX181 drape objs',[o.name[:40] for o in GO],flush=True)
dg=bpy.context.evaluated_depsgraph_get()
def top(x,y):
    best=None
    for o in GO:
        oe=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
        ok,loc,n,i=oe.ray_cast(inv@Vector((x,y,300)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(mw@loc).z
            if best is None or z>best: best=z
    return best
import numpy as _np
_DZ=_np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181f.npy')
def dtm(x,y):
    fx=(x+362.0)/0.5; fy=(-205.0-y)/0.5; i=int(min(max(fy,0),88)); j=int(min(max(fx,0),108)); a=fy-i; b=fx-j
    return float(_DZ[i,j]*(1-a)*(1-b)+_DZ[i,j+1]*(1-a)*b+_DZ[i+1,j]*a*(1-b)+_DZ[i+1,j+1]*a*b)
PAVE=[o for o in GO if re.match(r'^(WS167_Sprague_E_service|WS163_Lot3_aisle_S_drive|WS162_Lot3_S_end_apron)',o.name)]
LAWN=[o for o in GO if o not in PAVE]
def pavez(x,y):
    best=None
    for o in PAVE:
        oe=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
        ok,loc,n,i=oe.ray_cast(inv@Vector((x,y,300)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(mw@loc).z; best=z if best is None or z>best else best
    return best
def topn(x,y):
    hs=[top(x+dx,y+dy) for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3))]
    hs=[h for h in hs if h is not None]
    return max(hs) if hs else None
CTX=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Context_ground_beyond')]
def ctxz(x,y):
    best=None
    for o in CTX:
        oe=o.evaluated_get(dg); mw=o.matrix_world; inv=mw.inverted()
        ok,loc,n,i=oe.ray_cast(inv@Vector((x,y,300)),(inv.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(mw@loc).z; best=z if best is None or z>best else best
    return best
# Context_ground_beyond_data is a coarse filler that sits up to ~0.3 m above the 2023 LiDAR in the W drive band (x -356..-335, y -237..-226),
# where no fine ground patch exists: push its vertices under the new pavement (within the polygon + 1 m) to dtm - 0.08.
import numpy as _np2
def dist_out(x,y): return 0.0 if inside(x,y,Bp) else dist_b(x,y)
low=0
for o in CTX:
    mw=o.matrix_world; inv=mw.inverted()
    for v in o.data.vertices:
        w=mw@v.co
        if w.x<min(xs)-1.5 or w.x>max(xs)+1.5 or w.y<min(ys)-1.5 or w.y>max(ys)+1.5: continue
        if dist_out(w.x,w.y)>1.0: continue
        zt=dtm(w.x,w.y)-0.08
        if w.z>zt: v.co=inv@Vector((w.x,w.y,zt)); low+=1
    o.data.update()
print('FIX181 context ground verts lowered',low,flush=True)
dg=bpy.context.evaluated_depsgraph_get()
me=bpy.data.meshes.new(NAME); bm=bmesh.new(); vs=[]; miss=0; MISS=[]
Z0=[]; FL=[]
for v in V2:
    z=top(v.x,v.y)
    if z is None:
        miss+=1; MISS.append((round(v.x,1),round(v.y,1))); z=dtm(v.x,v.y)
        Z0.append(z); FL.append(pavez(v.x,v.y) or -1e9); continue
    Z0.append(z); FL.append(pavez(v.x,v.y) or -1e9)
# smooth the drape (a lot surface is a planar-ish pavement, not the 1 m LiDAR noise), then never go below the ground floor
NB=[set() for _ in V2]
for f in F2:
    for a in range(len(f)):
        i,j=f[a],f[(a+1)%len(f)]; NB[i].add(j); NB[j].add(i)
Zs=list(Z0)
for _ in range(int(__import__('os').environ.get('SMOOTH181','12'))):
    Zs=[0.5*Zs[i]+0.5*sum(Zs[j] for j in NB[i])/len(NB[i]) if NB[i] else Zs[i] for i in range(len(Zs))]
for k,v in enumerate(V2):
    d=dist_b(v.x,v.y); off=0.010+0.020*min(1.0,d/0.75)
    vs.append(bm.verts.new((v.x,v.y,max(Zs[k],FL[k])+off)))
for f in F2:
    try: bm.faces.new([vs[i] for i in f])
    except ValueError: pass
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    f.smooth=False
    for l in f.loops: l[uv].uv=(l.vert.co.x/4.0,l.vert.co.y/4.0)
bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new(NAME,me)
col=None
for o in GO:
    if o.name.startswith('WS167_ground') and o.users_collection: col=o.users_collection[0]
(col or bpy.context.scene.collection).objects.link(ob)
mat=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho')
if mat: me.materials.append(mat)
# push LiDAR lawn/ground patches under the new pavement (inside + 0.6 m outside), the #85/#86 pattern
dg=bpy.context.evaluated_depsgraph_get(); obe=ob.evaluated_get(dg)
BZ=[(Vector((p.x,p.y)),None) for p in R]
def asz(x,y):
    ok,loc,nn,i=obe.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
    if ok: return loc.z
    # outside: nearest boundary vertex of the new mesh
    best=None;bd=1e9
    for vv in me.vertices[:nb]:
        d=(vv.co.x-x)**2+(vv.co.y-y)**2
        if d<bd: bd=d; best=vv.co.z
    return best
pushed={}
for o in LAWN:
    mw=o.matrix_world; inv=mw.inverted(); k=0
    for v in o.data.vertices:
        w=mw@v.co
        if w.x<min(xs)-1 or w.x>max(xs)+1 or w.y<min(ys)-1 or w.y>max(ys)+1: continue
        do=dist_out(w.x,w.y)
        if do>1.5: continue
        a=asz(w.x,w.y)
        if a is None: continue
        zt=a-0.04 if do==0 else a-0.03+0.35*do   # lawn may rise from just under the pavement edge at <= 35 %, so the edge line is the polygon edge
        if w.z>zt: v.co=inv@Vector((w.x,w.y,zt)); k+=1
    o.data.update(); pushed[o.name[:28]]=k
print('FIX181 lawn pushed under',pushed,flush=True)
area=sum(p.area for p in me.polygons)
print('FIX181 lot36 verts %d faces %d area %.0f m2 miss %d mat %s'%(len(me.vertices),len(me.polygons),area,miss,mat.name if mat else None),flush=True)
# lawn-over-asphalt check (0.33 m grid): any drape object above the new surface?
dg=bpy.context.evaluated_depsgraph_get(); bad=0; n=0; BAD=[]
x=min(xs)
while x<=max(xs):
    y=min(ys)
    while y<=max(ys):
        if inside(x,y,Bp):
            n+=1; inv=ob.matrix_world.inverted()
            ok,loc,nn,i=ob.evaluated_get(dg).ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            t=top(x,y)
            if ok and t is not None and t>loc.z-0.002: bad+=1; BAD.append((round(x,1),round(y,1),round(t-loc.z,3)))
        y+=0.33
    x+=0.33
CB=0
for (bx,by,bd) in []: pass
print('FIX181 check samples %d ground-above-asphalt %d'%(n,bad),flush=True)

print('FIX181 MISS bbox',(min(m[0] for m in MISS),max(m[0] for m in MISS),min(m[1] for m in MISS),max(m[1] for m in MISS)) if MISS else None,flush=True)
print('FIX181 BAD',BAD[:40],flush=True)
# Context-ground poke check in the miss band (report)
cb=0; cn=0
x=-356.0
while x<=-335:
    y=-237.0
    while y<=-226:
        if inside(x,y,Bp):
            ok,loc,nn,i=ob.evaluated_get(dg).ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            c=ctxz(x,y); cn+=1
            if ok and c is not None and c>loc.z-0.002 and c-loc.z<0.3: cb+=1
        y+=0.25
    x+=0.25
print('FIX181 ctx-above-asphalt %d/%d'%(cb,cn),flush=True)

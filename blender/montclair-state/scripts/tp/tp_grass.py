# tp_grass (Nov 5 2026 ~12:45 AM ET, MAIN): grass clumps on the bare slopes round Bohn Hall x 175..280, y 295..445 (outside the TJ lawn), after tj_main.py's method.
# Tagged tp_obj -> removed by scripts/tp/tp_main.py REVERT=1 (tp_revert_all.sh). UNVERIFIED (no ground-cover reference; under-crown thinning approximated).
import bpy, os, math, random
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
col=bpy.data.collections['TP_Bohn_service_shafts_UNVERIFIED']
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
X0,X1,Y0,Y1=175,280,295,445
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
# blockers: visible meshes overlapping the box (no grass/terrain/trees/huge)
blk=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in GN or not o.visible_get(): continue
    n=o.name.lower()
    if 'grass' in n or 'tree' in n or 'skirt' in n or 'context' in n or 'terrain' in n: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; bx=[v.x for v in bb]; by=[v.y for v in bb]
    if max(bx)-min(bx)>600 or max(by)-min(by)>600: continue
    if min(bx)<X1 and max(bx)>X0 and min(by)<Y1 and max(by)>Y0:
        blk.append((o.evaluated_get(dg),o.matrix_world,(min(bx)-.3,max(bx)+.3,min(by)-.3,max(by)+.3),o.name))
print('TP blockers',len(blk),[b[3] for b in blk][:40])
def hit(lst,x,y):
    best=None
    for e,mw,*_ in lst:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
import json as _j
_W=_j.load(open('data/td/east_osm.json'))['ways']
LOT=[(0,0),(0.1,0),(0,0.1)]
LINES=[(_W[k]['pts'],{'546643370':4.2,'312841179':5.5,'843003380':3.5}.get(k,1.3)) for k,v in _W.items() if v['tags'].get('highway') in ('service','secondary')]
def _pip(x,y,P):
    ins=False
    for i in range(len(P)):
        x1,y1=P[i]; x2,y2=P[(i+1)%len(P)]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def _near(x,y):
    for P,w in LINES:
        for i in range(len(P)-1):
            ax,ay=P[i]; bx,by=P[i+1]; dx,dy=bx-ax,by-ay; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy+1e-9)))
            if math.hypot(ax+t*dx-x,ay+t*dy-y)<w: return True
    return False
WALKS=[k for k,v in _W.items() if v['tags'].get('highway') in ('footway','steps')]
LINES+= [(_W[k]['pts'],1.25) for k in WALKS]
LINES=[(P,w) for P,w in LINES if max(p[0] for p in P)>X0-5 and min(p[0] for p in P)<X1+5 and max(p[1] for p in P)>Y0-5 and min(p[1] for p in P)<Y1+5]
print('TP exclusion lines',len(LINES))
nex=0
random.seed(20261105)
TT=[(t[0],t[1]) for t in _j.load(open('data/tl/dorm_tree_tops_filtered.json'))]
pts=[]; rej=0; step=0.40
y=Y0
while y<Y1:
    x=X0
    while x<X1:
        px=x+random.uniform(-.17,.17); py=y+random.uniform(-.17,.17)
        if (px<215 and py>338) or _near(px,py): nex+=1; x+=step; continue   # x<215,y>338 already has TJ grass
        if any(abs(px-tx)<4 and abs(py-ty)<4 for tx,ty in TT) and random.random()>0.45: nex+=1; x+=step; continue   # thinner under tree crowns
        g=hit(gnd,px,py)
        if g is not None:
            bl=[b for b in blk if b[2][0]<px<b[2][1] and b[2][2]<py<b[2][3]]
            hb=hit(bl,px,py) if bl else None
            if hb is None or hb<g+0.02: pts.append((px,py,g))
            else: rej+=1
        x+=step
    y+=step
print('TP grass pts',len(pts),'excluded lot/paths',nex,'rejected under objects',rej)
src=bpy.data.objects['QV_Richardson_NW_lawn_grass_points_UNVERIFIED']
me=bpy.data.meshes.new('TP_Bohn_surround_grass_points_UNVERIFIED'); me.from_pydata(pts,[],[])
o=src.copy(); o.data=me; o.name='TP_Bohn_surround_grass_points_UNVERIFIED'; o.matrix_world=__import__('mathutils').Matrix.Identity(4)
for c in list(o.users_collection): c.objects.unlink(o)
col.objects.link(o); o['tp_obj']=1; o['UNVERIFIED']='grass round Bohn Hall slopes (was bare DTM); density from QV, thinned under LiDAR tree crowns'
for k in [k for k in o.keys() if k.startswith(('qv','qx','ti'))]: del o[k]

if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

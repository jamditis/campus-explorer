# ws93: WS77 island + lot-hole JOINT straightening (ws91 lesson 2). Straighten every WS77 boundary loop (RDP+projection),
# then move lot-sheet verts (WS74/75/76/80 + WS77 children) near the island foot by the SAME displacement (falloff), so no lot shows under the skirt.
import bpy,math,os,sys
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws91'); from straight91 import loops_of,straighten_loop
from mathutils import Vector
from mathutils.kdtree import KDTree
OB=bpy.data.objects
EPS=float(os.environ.get('EPS','0.10')); CL=float(os.environ.get('CLAMP','0.25')); R=float(os.environ.get('R','0.6')); RL=float(os.environ.get('RL','0.45'))
isl=[o for o in OB if o.type=='MESH' and o.name.startswith('WS77_lot_median_island') and not o.hide_render]
lots=[o for o in OB if o.type=='MESH' and not o.hide_render and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill'))]
print('P93 island',[o.name for o in isl]); print('P93 lots',[o.name for o in lots])
# 1. displacement field from all island boundary loops (world xy)
pts=[];dsp=[];per={}
for o in isl:
    mw=o.matrix_world; W=[mw@v.co for v in o.data.vertices]; F=[list(p.vertices) for p in o.data.polygons]; d={}
    for L in loops_of(F):
        P=[(W[i].x,W[i].y) for i in L]; Q,k,md=straighten_loop(P,EPS,CL)
        for j,i in enumerate(L):
            dx,dy=Q[j][0]-W[i].x,Q[j][1]-W[i].y; d[i]=(dx,dy); pts.append((W[i].x,W[i].y)); dsp.append((dx,dy))
    per[o.name]=(W,d)
kd=KDTree(len(pts))
for n,p in enumerate(pts): kd.insert(Vector((p[0],p[1],0)),n)
kd.balance()
FLAT=float(os.environ.get('FLAT','0.05'))
def field(x,y,Rr,flat=0.05):
    co,n,dd=kd.find(Vector((x,y,0)))
    if n is None or dd>Rr: return 0.0,0.0
    f=1.0 if dd<flat else max(0.0,1-(dd-flat)/(Rr-flat)); return dsp[n][0]*f,dsp[n][1]*f
def apply(o,W,fixed,Rr,flat=0.05):
    me=o.data; inv=o.matrix_world.inverted(); nz0=[p.normal.z for p in me.polygons]; mv=0; mx=0
    for i,v in enumerate(me.vertices):
        dx,dy=fixed[i] if i in fixed else field(W[i].x,W[i].y,Rr,flat)
        if abs(dx)+abs(dy)<1e-4: continue
        v.co=inv@Vector((W[i].x+dx,W[i].y+dy,W[i].z)); mv+=1; mx=max(mx,math.hypot(dx,dy))
    me.update(); bad=0
    for it in range(3):
        fl=[p for p,z0 in zip(me.polygons,nz0) if abs(z0)>0.5 and p.normal.z*z0<0.2*abs(z0)]
        if not fl: break
        for p in fl:
            for vi in p.vertices: me.vertices[vi].co=inv@W[vi]; bad+=1
        me.update()
    print('P93',o.name[:50],'moved',mv,'max %.2f'%mx,'revert',bad)
for o in isl:
    W,d=per[o.name]; apply(o,W,d,R)
for o in lots:
    mw=o.matrix_world; W=[mw@v.co for v in o.data.vertices]; apply(o,W,{},RL,FLAT)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('P93 SAVED')

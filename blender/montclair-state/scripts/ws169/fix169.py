# ws169: UNIFY #72 — lawn bank S of the Lot 3 W curb (y -234..-199) looked faceted/crumpled with a dark crease at its S end.
# Cause: WS162_Lot3_W_shoulder_lawn_bank_to_skirt_UNVERIFIED was a 3-column strip (t=4.2/10.2/13.2 m W of the curb line) whose outer rows took
# their z from the coarse 3DEP skirt as it was in ws162 (before #71 dropped the skirt) -> 0.3-0.5 m above the 2023 LiDAR toe (ws167c probes
# s-10 t8: 116.46 vs DTM 115.97), long thin facets and a step down onto the WS167 LiDAR ground patch.
# Evidence: 2023 NJ LiDAR class-2 DTM (scripts/ws162/dtm162.npy, 0.5 m): from the walk band's outer edge (~117.2) the ground falls ~1.4 m over
# ~5 m (about 1:3.5) to a flat toe ~115.7 (Sprague level) at ~9-10 m W of the curb; class-2 intensity (prep/ws163_lot3S/las163.npy) = grass
# (6-11k) from ~3 to ~10 m W of the curb, then the low-intensity (asphalt) service lane (WS167) at ~10-14 m.
# Build: same object, mesh replaced in place (keeps any references): rows every 0.5 m along the WEDGE line, 16 columns t=4.2..10.2 m;
# t=4.2 = walk outer edge (raw DTM+0.03, 1 cm under the walk as before); body = 3x3-smoothed DTM+0.03; outer 1.2 m eases to DTM+0.00 so the
# WS167 lane (DTM+0.03) laps on top. WS167 ground-patch vertices under the bank footprint are sunk 0.25 m (no poke-through on the concave toe).
# No depsgraph evaluation (memory balloon). Idempotent.
import bpy, bmesh, math, numpy as np
OB=bpy.data.objects
ZS=np.load('/workspace/nj-scenes/montclair-state/scripts/ws162/dtm162.npy')[1]; X0,Y1,R=-330.0,-165.0,0.5
K=np.array([[1,2,1],[2,4,2],[1,2,1]],float)/16.0
P_=np.pad(ZS,1,mode='edge'); ZM=sum(K[a,b]*P_[a:a+ZS.shape[0],b:b+ZS.shape[1]] for a in range(3) for b in range(3))
def samp(Z,x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),Z.shape[1]-2)); j=int(min(max(math.floor(fj),0),Z.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(Z[j,i]*(1-tx)*(1-ty)+Z[j,i+1]*tx*(1-ty)+Z[j+1,i]*(1-tx)*ty+Z[j+1,i+1]*tx*ty)
dz=lambda x,y: samp(ZS,x,y); dzs=lambda x,y: samp(ZM,x,y)
def ss(e0,e1,v): w=min(max((v-e0)/(e1-e0),0),1); return w*w*(3-2*w)
LS=[(-307.2,-234.0),(-306.4,-231.5),(-303.2,-215.0),(-301.4,-205.0),(-300.15,-198.75)]   # N end butts the WS166 bank first row (y -198.7)
pts=[]
for k in range(len(LS)-1):
    a=np.array(LS[k],float); b=np.array(LS[k+1],float); n=max(1,int(math.ceil(np.linalg.norm(b-a)/0.5)))
    for s_ in range(n): pts.append(a+(b-a)*s_/n)
pts.append(np.array(LS[-1],float))
TS=[4.2]+list(np.round(np.arange(4.6,10.21,0.4),2))
bm=bmesh.new(); rows=[]; dev=[]
for k,p in enumerate(pts):
    q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([-d[1],d[0]]); r=[]
    for t in TS:
        x,y=p+n*t
        wr=ss(4.2,5.0,t); base=dz(x,y)*(1-wr)+dzs(x,y)*wr
        z=base+0.03*(1-ss(9.0,10.2,t))
        r.append(bm.verts.new((x,y,z))); dev.append(z-dz(x,y))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(len(TS)-1): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
ob=OB['WS162_Lot3_W_shoulder_lawn_bank_to_skirt_UNVERIFIED']; me=ob.data
mats=list(me.materials); assert ob.matrix_world.is_identity or True
mw_inv=ob.matrix_world.inverted()
for v in bm.verts: v.co=mw_inv@v.co
bm.to_mesh(me); bm.free()
if not me.uv_layers: me.uv_layers.new(name='UVMap')
uv=me.uv_layers[0]; mw=ob.matrix_world
for lp in me.loops:
    pp=mw@me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(pp.x*0.25,pp.y*0.25)
for f in me.polygons: f.use_smooth=True
me.update()
print('BANK169 rows',len(rows),'cols',len(TS),'faces',len(me.polygons),'z-DTM min/max %.3f/%.3f'%(min(dev),max(dev)),'mats',[m.name for m in me.materials],flush=True)
# footprint test (wedge-t 4.0..9.9 between y -234.5 and -199)
from mathutils.geometry import intersect_point_line
def wedge_t(x,y):
    best=None
    for k in range(len(LS)-1):
        a=np.array(LS[k]);b=np.array(LS[k+1]); ab=b-a; u=np.dot(np.array([x,y])-a,ab)/np.dot(ab,ab)
        if 0<=u<=1:
            dd=ab/np.linalg.norm(ab); nn=np.array([-dd[1],dd[0]]); t=float(np.dot(np.array([x,y])-a,nn))
            best=t if best is None else best
    return best
pa=OB.get('WS167_ground_W_of_Lot3_bank_Sprague_side_LiDAR2023_1m'); sunk=0
if pa:
    pm=pa.matrix_world; pi=pm.inverted()
    for v in pa.data.vertices:
        w=pm@v.co; t=wedge_t(w.x,w.y)
        if t is not None and 3.6<t<9.9 and w.z>dz(w.x,w.y)-0.1:
            w.z-=0.25; v.co=pi@w; sunk+=1
    pa.data.update()
print('PATCH sunk',sunk,flush=True)
# what lies around the S end (bbox overlap), for the log
near=[]
for o in OB:
    if o.type!='MESH': continue
    bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
    if min(c.x for c in bb)<-300 and max(c.x for c in bb)>-318 and min(c.y for c in bb)<-230 and max(c.y for c in bb)>-240 and (max(c.x for c in bb)-min(c.x for c in bb))<400:
        near.append(o.name[:60])
print('NEAR_S_END',near,flush=True)

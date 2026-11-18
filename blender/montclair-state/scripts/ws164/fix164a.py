# ws164 UNIFY #68 — dark shards on the bank N of the Normal Ave W N walk (x -296..-280).
# Probe (scripts/ws164/probe164.py on ws163c): (a) WS110_ground_patch_S_of_y-238 has saw-teeth there: up to +0.6 m above the 2023 LiDAR
# class-2 ground at x -282 y -255 (patch 118.04 vs LiDAR ~117.4) next to verts pushed 6 cm under the walk -> 55 deg facets (nz 0.56);
# (b) Context_skirt topmost at y -254.75, x -287..-290.5 because the WS163 GN drops it only 0.12 m under a frozen copy of those teeth.
# Real ground (LiDAR) is a gentle ~10 cm/m bank rising N. Fix: regrade the WS110 patch in the zone to the LiDAR DTM -3 cm (feathered),
# keep it 6 cm under every WS163 surface, rebuild the hidden skirt target from the regraded surfaces, deeper drop (0.45 m) in the zone.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
P='/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/'
D=np.load(P+'dtm163.npy')[0].copy(); X0,Y0,R=-350.0,-290.0,0.5
for j,i in zip(*np.nonzero(np.isnan(D))):
    for rr in range(1,14):
        sub=D[max(j-rr,0):j+rr+1,max(i-rr,0):i+rr+1]
        if np.isfinite(sub).any(): D[j,i]=float(np.nanmedian(sub)); break
Dp=np.pad(D,1,mode='edge'); D=sum(Dp[1+a:1+a+D.shape[0],1+b:1+b+D.shape[1]] for a in (-1,0,1) for b in (-1,0,1))/9.0     # 1.5 m smoothing: clean bank, no cell noise
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
def ramp(v,a,b,f): return min(max(min(v-a,b-v)/f+1.0,0.0),1.0)
ZX=(-302.0,-270.0); ZY=(-262.0,-240.5); FE=2.5
class _C: pass
col=_C(); col.objects=[o for o in OB if o.name.startswith('WS163_')]
surf=[o for o in col.objects if o.type=='MESH' and not o.name.startswith(('WS163_skirt_target','WS163_ground_patch'))]
V=[];F=[]
for o in surf:
    b=len(V); V+=[o.matrix_world@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
T=BVHTree.FromPolygons(V,F)
def ztop(x,y):
    best=None
    for ddx,ddy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
        h=T.ray_cast(Vector((x+ddx,y+ddy,200)),Vector((0,0,-1)))
        if h[0] is not None: best=h[0].z if best is None else min(best,h[0].z)
    return best
pa=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; mw=pa.matrix_world; mi=mw.inverted(); n=0; dmax=0
for v in pa.data.vertices:
    p=mw@v.co; w=ramp(p.x,*ZX,FE)*ramp(p.y,*ZY,FE)
    if w<=0: continue
    z=p.z+(dz(p.x,p.y)-0.03-p.z)*w; zt=ztop(p.x,p.y)
    if zt is not None: z=min(z,zt-0.06)
    dmax=max(dmax,abs(z-p.z))
    pass
    p.z=z; v.co=mi@p; n+=1
pa.data.update(); print('REGRADE WS110 verts',n,'max change',round(dmax,3))
# rebuild hidden skirt target (as fix163b) from the regraded surfaces
tgt=OB['WS163_skirt_target_hidden']; tb=bmesh.new()
srcs=[OB['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED'],pa]+[o for o in col.objects if o.type=='MESH' and not o.name.startswith(('WS163_skirt_target','WS163_ground_patch','WS163_walk_back_lawn_lip'))]+[o for o in OB if o.name.startswith('WS162_') and o.type=='MESH']
for o in srcs:
    m=o.matrix_world
    for p in o.data.polygons:
        cs=[m@o.data.vertices[i].co for i in p.vertices]
        if all(-352<c.x<-266 and -282<c.y<-228 for c in cs): tb.faces.new([tb.verts.new(c) for c in cs])
tb.to_mesh(tgt.data); tb.free(); me=tgt.data
a=me.attributes.get('wv_in') or me.attributes.new('wv_in','FLOAT','POINT')
val=[0.10+0.35*ramp(v.co.x,*ZX,3.0)*ramp(v.co.y,-264.0,-240.5,3.0) for v in me.vertices]   # target has identity matrix
me.attributes['wv_in'].data.foreach_set('value',val); me.update(); tgt.update_tag()
print('TARGET faces',len(me.polygons),'deep verts',sum(x>0.44 for x in val))

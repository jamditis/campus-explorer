# ws167: UNIFY #71 — W of Lot 3 N (y -201..-166) the far-field 3DEP skirt sat 1.5-1.7 m above the 2023 LiDAR toe; the lower bank,
# the Sprague service lane and the Sprague E bleachers were missing.
# Evidence: 2023 NJ LiDAR class-2 DTM (prep/ws163_lot3S/dtm163.npy) + class-2 intensity (las163.npy): a ~4 m low-intensity (asphalt) lane
# runs diagonally W of the bank (x -306..-303 at y -166 -> x -314..-309 at y -199); W of it flat ground ~115.7 (Sprague Field side).
# Non-ground (class 1) returns 0-2 m above the bank from ~1.6 to ~8.6 m W of the curb = low aluminium bleachers set on the bank; the 2020 NJOGIS
# ortho (prep/ws162_lot3/ortho_lot3*_grid.png) shows white seat rows there with brown breaks at y ~-181 and ~-199 (aisles, UNVERIFIED).
# Build: (1) 1 m LiDAR ground patch W of the bank (lawn), (2) straight lane ribbon fitted to the intensity cells (asphalt), (3) bleachers
# (11 rows, 0.6 m tread, aluminium planks, galvanised legs, top guard rail; row levels from the DTM), (4) hidden target + skirt GN drop.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
P='/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/'
D=np.load(P+'dtm163.npy')[0].copy(); X0,Y0,R=-350.0,-290.0,0.5
for j,i in zip(*np.nonzero(np.isnan(D))):
    if not (Y0+j*R>-215 and Y0+j*R<-150): continue
    for rr in range(1,14):
        sub=D[max(j-rr,0):j+rr+1,max(i-rr,0):i+rr+1]
        if np.isfinite(sub).any(): D[j,i]=float(np.nanmedian(sub)); break
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
col=bpy.data.collections.get('WS167_Sprague_E_bank_lane_bleachers')
if not col: col=bpy.data.collections.new('WS167_Sprague_E_bank_lane_bleachers'); bpy.context.scene.collection.children.link(col)
# curb chord (Lot 3 W curb, ws162 LS) and its W normal
C0=np.array([-300.2,-198.7]); C1=np.array([-296.4,-171.5]); cd=(C1-C0)/np.linalg.norm(C1-C0); cn=np.array([-cd[1],cd[0]])
if cn[0]>0: cn=-cn
def tW(x,y): return float(np.dot(np.array([x,y])-C0,cn))
# lane fit from intensity
L=np.load(P+'las163.npy'); m=(L[:,3]==2)&(L[:,1]>-202)&(L[:,1]<-165)&(L[:,0]>-330)&(L[:,0]<-296); S=L[m]
xs=[];ys=[]
for y in np.arange(-201.5,-165.5,1.0):
    for x in np.arange(-322,-298,1.0):
        k=(S[:,0]>=x)&(S[:,0]<x+1)&(S[:,1]>=y)&(S[:,1]<y+1)
        if k.sum()>3 and np.median(S[k,4])<4300 and 5<tW(x+0.5,y+0.5)<18: xs.append(x+0.5); ys.append(y+0.5)
xs=np.array(xs); ys=np.array(ys); tl=np.array([tW(a,b) for a,b in zip(xs,ys)])
# lane centre as t = a + b*along
al=np.array([float(np.dot(np.array([a,b])-C0,cd)) for a,b in zip(xs,ys)])
b_,a_=np.polyfit(al,tl,1); res=tl-(a_+b_*al); wl=float(np.percentile(np.abs(res),90))*2+1.0
print('LANE fit t=%.2f+%.4f*s cells %d width~%.2f'%(a_,b_,len(xs),wl),flush=True)
LW=4.0
def P2(s,t): q=C0+cd*s+cn*t; return float(q[0]),float(q[1])
S0,S1=-3.0,34.0   # along-chord range (y ~ -201.6 .. -165)
lawn=bpy.data.materials.get('COLE_lawn_post2020_bs'); asm=bpy.data.materials.get('WS27_CollegeAve_asphalt_2020ortho')
def mk(name,bm,mats):
    for f in bm.faces:
        f.normal_update()
        if f.normal.z<0: f.normal_flip()
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for mt in mats: me.materials.append(mt)
    if me.polygons:
        uv=me.uv_layers.new(name='UVMap')
        for lp in me.loops:
            p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.25,p.y*0.25)
    ob=OB.new(name,me); col.objects.link(ob); return ob

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
for o in [o for o in OB if o.name.startswith('WS167_')]: OB.remove(o)
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
# (2) lane ribbon
bm=bmesh.new(); rows=[]
for s in np.arange(S0,S1+0.01,1.0):
    tc=a_+b_*s; r=[]
    for t in (tc-LW/2,tc-LW/2+1,tc,tc+LW/2-1,tc+LW/2):
        x,y=P2(s,t); r.append(bm.verts.new((x,y,dz(x,y)+0.03)))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(4): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
lane=mk('WS167_Sprague_E_service_lane_LiDAR2023_intensity_UNVERIFIEDsection',bm,[asm])
# (1) ground patch: lawn W of the bank (t > 8.3) excluding nothing (lane sits 3 cm above), 1 m, z = DTM-0.02
bm=bmesh.new(); G={}
TS=list(np.arange(8.3,52.0,1.0))
for s in np.arange(S0,S1+0.01,1.0):
    for t in TS:
        x,y=P2(s,t); G[(round(s,2),round(t,2))]=bm.verts.new((x,y,dz(x,y)-0.02))
SS=list(np.arange(S0,S1+0.01,1.0))
for i in range(len(SS)-1):
    for j in range(len(TS)-1):
        a=G[(round(SS[i],2),round(TS[j],2))];b=G[(round(SS[i],2),round(TS[j+1],2))];c=G[(round(SS[i+1],2),round(TS[j+1],2))];d=G[(round(SS[i+1],2),round(TS[j],2))]
        bm.faces.new((a,b,c,d))
patch=mk('WS167_ground_W_of_Lot3_bank_Sprague_side_LiDAR2023_1m',bm,[lawn])
# (3) bleachers
alu=bpy.data.materials.get('WS167_bleacher_aluminium') or bpy.data.materials.new('WS167_bleacher_aluminium'); alu.use_nodes=True
bs=alu.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(0.62,0.63,0.64,1); bs.inputs['Metallic'].default_value=0.85; bs.inputs['Roughness'].default_value=0.38
gal=bpy.data.materials.get('WS167_bleacher_galv_steel') or bpy.data.materials.new('WS167_bleacher_galv_steel'); gal.use_nodes=True
bg=gal.node_tree.nodes.get('Principled BSDF'); bg.inputs['Base Color'].default_value=(0.42,0.43,0.44,1); bg.inputs['Metallic'].default_value=0.7; bg.inputs['Roughness'].default_value=0.55
def box(bm,cs,ce,t0,t1,z0,z1,mi):
    # cs..ce along chord, t0..t1 across (W positive), z0..z1
    v=[]
    for (s,t) in ((cs,t0),(ce,t0),(ce,t1),(cs,t1)):
        x,y=P2(s,t); v.append((x,y))
    lo=[bm.verts.new((x,y,z0)) for x,y in v]; hi=[bm.verts.new((x,y,z1)) for x,y in v]
    fs=[bm.faces.new(hi),bm.faces.new(lo[::-1])]
    for k in range(4): fs.append(bm.faces.new((lo[k],lo[(k+1)%4],hi[(k+1)%4],hi[k])))
    for f in fs: f.material_index=mi
SECT=[(-1.2,16.6),(17.8,33.5)]   # along-chord; aisles near y -199 and -181 (ortho brown breaks, UNVERIFIED)
NR=11; T_TOP=1.6; TREAD=0.6
bm=bmesh.new(); info=[]
for (sa,sb) in SECT:
    for k in range(NR):
        t=T_TOP+k*TREAD            # k=0 top row (nearest the curb)
        g=np.mean([dz(*P2(s,t+0.3)) for s in np.linspace(sa,sb,12)])
        fb=g+0.22 if k<NR-1 else g+0.18
        info.append(round(fb-g,2))
        # footboard (front of the row, W side) + seat plank 0.43 above at the back (E side)
        box(bm,sa,sb,t+0.25,t+0.55,fb-0.04,fb,0)
        box(bm,sa,sb,t+0.02,t+0.27,fb+0.40,fb+0.44,0)
        # legs under seat + footboard every 1.8 m
        for s in np.arange(sa+0.3,sb,1.8):
            gs=dz(*P2(s,t+0.15)); box(bm,s,s+0.06,t+0.12,t+0.18,gs-0.05,fb+0.40,1)
            gf=dz(*P2(s,t+0.45)); box(bm,s,s+0.06,t+0.42,t+0.48,gf-0.05,fb-0.04,1)
    # top guard rail behind the top row (E side, t < T_TOP)
    gt=np.mean([dz(*P2(s,T_TOP+0.3)) for s in np.linspace(sa,sb,12)])+0.22
    for s in np.arange(sa,sb+0.01,(sb-sa)/round((sb-sa)/1.8)):
        box(bm,s-0.025,s+0.025,T_TOP-0.05,T_TOP,dz(*P2(s,T_TOP))-0.05,gt+1.07,1)
    for hz in (0.53,1.07): box(bm,sa,sb,T_TOP-0.06,T_TOP+0.0,gt+hz-0.04,gt+hz,0)
ble=mk('WS167_Sprague_E_bleachers_on_bank_LiDAR2023_ortho2020_UNVERIFIEDdetails',bm,[alu,gal])
print('BLEACH rows',NR,'clear',info[:NR],'faces',len(ble.data.polygons),flush=True)
# (4) hidden skirt target + GN drop
tb=bmesh.new()
srcs=[patch,lane]+[o for o in OB if o.name.startswith('WS166_Lot3_W_shoulder_bank')]
for o in srcs:
    mw=o.matrix_world
    for p in o.data.polygons: tb.faces.new([tb.verts.new(mw@o.data.vertices[i].co) for i in p.vertices])
tm=bpy.data.meshes.new('WS167_skirt_target_hidden'); tb.to_mesh(tm); tb.free()
a=tm.attributes.new('wv_in','FLOAT','POINT'); a.data.foreach_set('value',[0.10]*len(tm.vertices))
tgt=OB.new('WS167_skirt_target_hidden',tm); col.objects.link(tgt); tgt.hide_render=True; tgt.hide_viewport=True
xs_=[v.co.x for v in tm.vertices]; ys_=[v.co.y for v in tm.vertices]
sk=OB['Context_skirt_3DEP_ortho_4km']
for m_ in [m_ for m_ in sk.modifiers if m_.name.startswith('WS167_')]: sk.modifiers.remove(m_)
ng=bpy.data.node_groups['WS163_skirt_under_normalave_W'].copy(); ng.name='WS167_skirt_under_Lot3N_W'
N=ng.nodes
N['Compare'].inputs[1].default_value=min(xs_)-2; N['Compare.001'].inputs[1].default_value=max(xs_)+1
N['Compare.002'].inputs[1].default_value=min(ys_)-1; N['Compare.003'].inputs[1].default_value=max(ys_)+1
N['Object Info'].inputs['Object'].default_value=tgt
mod=sk.modifiers.new('WS167_skirt_under_Lot3N_W','NODES'); mod.node_group=ng
print('GN bounds',round(min(xs_),1),round(max(xs_),1),round(min(ys_),1),round(max(ys_),1),flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for s,t in ((0,9),(10,12),(20,10),(30,9),(5,20),(25,30),(15,45),(15,5),(30,4)):
    x,y=P2(s,t); r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1))); print('PROBE s%d t%d (%.1f,%.1f)'%(s,t,x,y),r[4].name[:45] if r[0] else None,round(r[1].z,2) if r[0] else None,'dtm',round(dz(x,y),2),flush=True)
# edge check: skirt just outside the patch W edge
for s in (0,15,30):
    for t in (52.5,54):
        x,y=P2(s,t); r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1))); print('EDGE',s,t,r[4].name[:30] if r[0] else None,round(r[1].z,2) if r[0] else None,'dtm',round(dz(x,y),2),flush=True)


def cam(name,p,look,lens=28):
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_start=0.1; c.clip_end=3000
    o=OB.new(name,c); col.objects.link(o); o.location=p
    o.rotation_euler=(Vector(look)-Vector(p)).to_track_quat('-Z','Y').to_euler(); return o
x,y=P2(-8,a_); cam('WS167_CAM_eye_lane_N_along_bleachers_from_S',(x,y,dz(x,y)+1.65),(*P2(14,a_-3),dz(*P2(14,a_-3))+1.0),24)
x,y=P2(10,20); xl,yl=P2(13,4); cam('WS167_CAM_closeup_bleachers_from_W_turf',(x,y,dz(x,y)+1.7),(xl,yl,dz(xl,yl)+0.8),30)
x,y=P2(40,a_+3); xl,yl=P2(14,a_-3); cam('WS167_CAM_eye_lane_S_from_N',(x,y,dz(x,y)+1.65),(xl,yl,dz(xl,yl)+0.9),26)
print('CAMS ok',flush=True)


# ws186 (Nov 16 ~11:45 AM ET) — UNIFY #90 + fix185 review fixes. Chain AFTER ws185/fix185.py.
# (a) fix185 grass strip lay 1-3 cm ABOVE the Lot 36 asphalt where the lot reaches N of the fitted lot-edge line (probe186 at (-335.5,-228.5)):
#     strip verts over the asphalt go 2 cm under it (paving wins; the strip only shows where there is no asphalt).
# (b) UNIFY #90: the ws184 hole-fill sheet on the bank W of the Lot 3 S ramp stood as a flat card with 4-5 cm lips against the WS163 patch /
#     WS169c bridge (1 m DTM vs 0.25 m DTM). Rebuild it as ONE bank surface x -315.5..-309.5, y -239..-232 on the 2023 DTM; neighbour lawn
#     verts inside it (0.5 m in from its edge) go 3 cm under it; its own boundary ring is set flush (-5 mm) to the neighbour top so no lip shows;
#     anything under the paved drive/apron goes 3 cm under the paving.
# (c) report steep faces (|nz|<0.5) of the Lot 36 asphalt / grass strip (the 'vertical wedge' at the NW lobe in the ws184a W eye view).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
def first(prefix): return next((o for o in bpy.data.objects if o.name.startswith(prefix)),None)
LOT=first('WS181_Lot36_asphalt'); GS=first('WS185_Lot36_N_grass_strip')
if LOT and GS:
    tl=bvh(LOT); M=GS.matrix_world; Mi=M.inverted(); c=0
    for v in GS.data.vertices:
        w=M@v.co; h=tl.ray_cast(Vector((w.x,w.y,w.z+1.0)),Vector((0,0,-1)),2.0)
        if h[0] is not None and w.z>h[0].z-0.02: v.co=Mi@Vector((w.x,w.y,h[0].z-0.02)); c+=1
    GS.data.update(); print('FIX186 grass strip verts under lot asphalt',c,flush=True)
if LOT:
    bm=bmesh.new(); bm.from_mesh(LOT.data); M=LOT.matrix_world
    ed=[e for e in bm.edges if all(-321<(M@v.co).x<-315 and -219<(M@v.co).y<-210 for v in e.verts)]
    bmesh.ops.dissolve_degenerate(bm,dist=0.08,edges=ed)
    bad=[f for f in bm.faces if (M.to_3x3()@f.normal).normalized().z<0.5 and f.calc_area()<0.02]
    bmesh.ops.delete(bm,geom=bad,context='FACES'); bm.to_mesh(LOT.data); bm.free(); LOT.data.update()
    print('FIX186 lot NE slivers removed',len(bad),flush=True)
# (c) steep-face report
for o in (LOT,GS):
    if not o: continue
    M=o.matrix_world; st=[]
    for p in o.data.polygons:
        n=(M.to_3x3()@p.normal).normalized(); cc=M@p.center
        if abs(n.z)<0.5: st.append((round(cc.x,1),round(cc.y,1),round(cc.z,2),round(n.z,2),round(p.area,3)))
    print('FIX186 steep faces',o.name[:30],len(st),st[:12],flush=True)
# (b) UNIFY #90
DZ=np.load('/workspace/nj-scenes/montclair-state/prep/ws185_lot36N/dtm185_0p25m.npy'); X0,Y1,RS=-352.,-190.,0.25
import os
DZ2=None
for cand in ('prep/ws184_lot3S/dtm184_0p25m.npy','prep/ws171_lot36/dtm171_0p25m.npy'):
    pass
def dtmz(x,y):
    fx=(x-X0)/RS; fy=(Y1-y)/RS
    if not (0<=fx<DZ.shape[1]-1 and 0<=fy<DZ.shape[0]-1): return None
    j,i=int(fx),int(fy); a,b=fy-i,fx-j; q=DZ[i:i+2,j:j+2]
    if np.isnan(q).any(): return None
    return float(q[0,0]*(1-a)*(1-b)+q[0,1]*(1-a)*b+q[1,0]*a*(1-b)+q[1,1]*a*b)
OLD=first('WS184_Lot3_S_drive_W_edge_lawn_fill')
NB=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS163_ground_patch_W_of_WS110','WS169c','WS167_ground_W','WS162_Lot3_W_shoulder_lawn'))]
PV=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS162_Lot3_W_walk_band','WS163_Lot3_aisle_S_drive','WS162_Lot3_S_end_apron','WS170b_Lot3_S_end_curb','WS162_Lot3_asphalt','WS181_Lot36_asphalt'))]
if OLD:
    # (b0) the step the W eye view shows at the bank toe: WS162 shoulder lawn ends at y ~-231.8 ON the 2023 DTM while the WS169c lawn bridge
    #      S of it sits 6-15 cm under the DTM (probe186b) -> re-seat WS169c / WS163-patch verts in x -316..-309.5, y -234.5..-230.5 onto DTM-1 cm
    #      (never above paving -3 cm). Then the new bank sheet's flush edge follows the corrected surface.
    _D0=np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181_0p5m.npy')
    def _d0(x,y):
        c=int(round((x+355)/0.5)); r=int(round((-200-y)/0.5)); w=_D0[max(r-1,0):r+2,max(c-1,0):c+2]
        return float(np.nanmean(w)) if np.isfinite(w).any() else None
    _TP=[bvh(o) for o in PV]; rs={}
    for o in NB:
        if not o.name.startswith(('WS169c','WS163_ground_patch_W_of_WS110')): continue
        M=o.matrix_world; Mi=M.inverted(); c=0
        for v in o.data.vertices:
            w=M@v.co
            if not (-316<w.x<-309.5 and -234.5<w.y<-230.5): continue
            zd=_d0(w.x,w.y)
            if zd is None or w.z>=zd-0.03: continue
            zt=zd-0.01
            for t in _TP:
                h=t.ray_cast(Vector((w.x,w.y,140.0)),Vector((0,0,-1)),60.0)
                if h[0] is not None: zt=min(zt,h[0].z-0.03)
            if zt>w.z: v.co=Mi@Vector((w.x,w.y,zt)); c+=1
        if c: o.data.update(); rs[o.name[:24]]=c
    print('FIX186 #90 toe lawn re-seated on DTM',rs,flush=True)
    TN={o.name:bvh(o) for o in NB}; TP=[bvh(o) for o in PV]
    def top(T,x,y):
        best=None
        for t in T:
            h=t.ray_cast(Vector((x,y,140.0)),Vector((0,0,-1)),60.0)
            if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
        return best
    _D=np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181_0p5m.npy')
    def dtm5(x,y):   # 2023 DTM 0.5 m (x0 -355, y0 -200), 3x3 nan-mean = the same surface fix184 seated the drive on
        c=int(round((x+355)/0.5)); r=int(round((-200-y)/0.5)); w=_D[max(r-1,0):r+2,max(c-1,0):c+2]
        return float(np.nanmean(w)) if np.isfinite(w).any() else None
    def near(T,x,y,zref):   # neighbour surface hit closest to zref (NOT the max: stacked bank sheets differ by up to 0.5 m)
        best=None
        for t in T:
            z=140.0
            while True:
                h=t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),60.0)
                if h[0] is None: break
                if best is None or abs(h[0].z-zref)<abs(best-zref): best=h[0].z
                z=h[0].z-0.002
        return best
    XA,XB,YA,YB,SS=-315.5,-307.0,-239.0,-231.5,0.25   # ws186 top-view debug: void (black) between the walk band S end and the drive NW corner ~(-308.5,-234) -> sheet reaches x -307
    xs=np.arange(XA,XB+1e-6,SS); ys=np.arange(YA,YB+1e-6,SS); nx=len(xs); vs=[]; fs=[]; nd=0; ne=0; npv=0; nl=0
    for y in ys:
        for x in xs:
            edge=(x<XA+1e-6 or x>XB-1e-6 or y<YA+1e-6 or y>YB-1e-6)
            zd=dtm5(x,y)
            if zd is None: nd+=1
            tn=near(TN.values(),x,y,zd if zd is not None else 116.5)
            if zd is None: zd=tn if tn is not None else 116.5
            z=zd+0.01
            if tn is not None:
                d=min(x-XA,XB-x,y-YA,YB-y); wgt=min(1.0,d/1.0)
                z=(tn-0.005) if edge else (tn+0.01+wgt*(zd-tn))
                if edge: ne+=1
            tp=top(TP,x,y)
            if tp is not None and z>tp-0.03: z=tp-0.03; npv+=1
            elif tp is None:   # grass meets the asphalt edge: lift to the nearest paving point within 0.45 m (kills the dark slit under the drive edge)
                for t in TP:
                    h=t.find_nearest(Vector((x,y,z)),0.45)
                    if h[0] is not None and h[0].z-0.015>z: z=h[0].z-0.015; nl+=1; break
            vs.append((float(x),float(y),float(z)))
    for j in range(len(ys)-1):
        for i in range(nx-1): a=j*nx+i; fs.append((a,a+1,a+nx+1,a+nx))
    me=OLD.data; mats=list(me.materials)
    nm=bpy.data.meshes.new('WS186_Lot3_S_bank_lawn_DTM2023_UNIFY90'); nm.from_pydata(vs,[],fs); nm.update()
    for p in nm.polygons: p.use_smooth=True
    for m in mats: nm.materials.append(m)
    OLD.data=nm; OLD.matrix_world.identity(); OLD.name='WS186_Lot3_S_bank_lawn_DTM2023_UNIFY90'
    tf=BVHTree.FromPolygons([Vector(v) for v in vs],fs); cnt={}
    for o in NB:
        M=o.matrix_world; Mi=M.inverted(); c=0
        for v in o.data.vertices:
            w=M@v.co
            if not (XA+0.5<w.x<XB-0.5 and YA+0.5<w.y<YB-0.5): continue
            h=tf.ray_cast(Vector((w.x,w.y,w.z+2.0)),Vector((0,0,-1)),4.0)
            if h[0] is not None and w.z>h[0].z-0.03: v.co=Mi@Vector((w.x,w.y,h[0].z-0.03)); c+=1
        if c: o.data.update(); cnt[o.name[:26]]=c
    # lawn poking through the walk band's S end (top-view debug 1150): any lawn vert in the box under a paving surface -> 3 cm under it
    pu={}
    for o in NB:
        M=o.matrix_world; Mi=M.inverted(); c=0
        for v in o.data.vertices:
            w=M@v.co
            if not (XA-1<w.x<XB+1 and YA-1<w.y<YB+2): continue
            tp=top(TP,w.x,w.y)
            if tp is not None and w.z>tp-0.03 and w.z<tp+0.5: v.co=Mi@Vector((w.x,w.y,tp-0.03)); c+=1
        if c: o.data.update(); pu[o.name[:24]]=c
    print('FIX186 #90 lawn under paving',pu,flush=True)
    print('FIX186 #90 bank sheet verts %d faces %d nodtm %d edge-flush %d under-paving %d lifted-to-paving-edge %d neighbours pushed %s'%(len(vs),len(fs),nd,ne,npv,nl,cnt),flush=True)
else: print('FIX186 #90 SKIPPED fill missing',flush=True)

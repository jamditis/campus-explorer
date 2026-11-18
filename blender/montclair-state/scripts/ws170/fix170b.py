# ws170b: UNIFY #76 — Lot 3 S end E of the aisle S drive.
# Evidence: 2023 LiDAR class-2 intensity at x -304/-301: asphalt ~800-1300 to y -234.0/-234.5, then a bright 5000-7000 band
# 1.4-1.5 m wide (concrete) to y -235.5, ground rising ~0.3 m S of it; 2020 NJOGIS ortho shows a light concrete corner at (-304.5,-233.5)
# with tree-shaded lawn S of it (x -304..-294). So the lot ends in a curb + concrete strip, NOT an asphalt apron diving into the lawn.
# Fix: (1) delete WS162 S-end apron faces E of the drive (x > -303.4), lift the rest to DTM+0.02 (under the drive);
# (2) straight curb + concrete strip along the lot S end x -304.6..-298.8 (E end UNVERIFIED: tree canopy hides LiDAR/ortho beyond);
# (3) lawn patches (WS163 W-of-WS110 / WS110 S-of-y-238) in x -320..-294, y -243..-231 regraded to DTM-0.03 (seam line + trough gone),
#     and lifted to strip top -0.03 within 1.2 m S of the strip.
import bpy, bmesh, math, numpy as np
OB=bpy.data.objects
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/dtm163.npy')[0].copy(); X0,Y0,R=-350.0,-290.0,0.5
def dz(x,y,r0=1):
    i=int((x-X0)/R); j=int((y-Y0)/R)
    for r in range(r0,8):
        s=D[max(j-r,0):j+r+1,max(i-r,0):i+r+1]
        if np.isfinite(s).sum()>=3: return float(np.nanmedian(s))
    return float('nan')
for o in [o for o in OB if o.name.startswith('WS170b_')]: OB.remove(o)
# (1) apron
ap=OB.get('WS162_Lot3_S_end_apron_feather_UNVERIFIED')
if ap:
    bm=bmesh.new(); bm.from_mesh(ap.data); mw=ap.matrix_world; inv=mw.inverted()
    kill=[f for f in bm.faces if (mw@f.calc_center_median()).x>-303.4]
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    for v in bm.verts:
        w=mw@v.co; z=dz(w.x,w.y)
        if z==z: w.z=z+0.02; v.co=inv@w
    bm.to_mesh(ap.data); bm.free(); print('APRON kept faces',len(ap.data.polygons),'deleted',len(kill),flush=True)
# (2) curb + strip: N edge y = -234.0 - 0.125*(x+307.2), 0.15 m curb + 1.3 m strip
def yN(x): return -234.0-0.125*(x+307.2)
XS=list(np.arange(-304.6,-298.79,0.4)); nrm=np.array([0.125,-1.0])/math.hypot(0.125,1.0)  # points S (into strip)
def zt(x):
    vals=[dz(x,yN(x)-o) for o in (0.3,0.7,1.1)]; return float(np.nanmedian(vals))+0.15
bm=bmesh.new(); T=[0.0,0.15,1.45]; G={}
for i,x in enumerate(XS):
    zz=zt(x)
    for k,t in enumerate(T):
        px,py=x+nrm[0]*t, yN(x)+nrm[1]*t
        G[(i,k,'t')]=bm.verts.new((px,py,zz)); G[(i,k,'b')]=bm.verts.new((px,py,zz-0.35))
for i in range(len(XS)-1):
    for k in range(len(T)-1): bm.faces.new((G[(i,k,'t')],G[(i+1,k,'t')],G[(i+1,k+1,'t')],G[(i,k+1,'t')]))
    bm.faces.new((G[(i,0,'b')],G[(i+1,0,'b')],G[(i+1,0,'t')],G[(i,0,'t')]))      # curb face (N)
    bm.faces.new((G[(i,2,'t')],G[(i+1,2,'t')],G[(i+1,2,'b')],G[(i,2,'b')]))      # back (S)
for i in (0,len(XS)-1):
    for k in range(len(T)-1): bm.faces.new((G[(i,k,'b')],G[(i,k,'t')],G[(i,k+1,'t')],G[(i,k+1,'b')]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS170b_Lot3_S_end_curb_strip'); bm.to_mesh(me); bm.free()
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED') or bpy.data.materials.new('WS27_curb_concrete_UNVERIFIED'); me.materials.append(cm)
col=(OB['WS162_Lot3_S_end_apron_feather_UNVERIFIED'].users_collection[0] if ap else bpy.context.scene.collection)
ob=OB.new('WS170b_Lot3_S_end_curb_concrete_strip_LiDAR2023_int_UNVERIFIED_E_end',me); col.objects.link(ob)
# (3) lawn regrade
n=0
for nm in ('WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED'):
    o=OB.get(nm)
    if not o: continue
    mw=o.matrix_world; inv=mw.inverted()
    for v in o.data.vertices:
        w=mw@v.co
        if not (-320<w.x<-294 and -243<w.y<-231): continue
        z=dz(w.x,w.y,4)
        if z!=z: continue
        tgt=z-0.03
        if (-313.6<w.x<-302.4) or w.y>-235.8:  # under drive/lot asphalt: never above the local DTM-0.03 (SELF_REVIEW 6)
            zl=dz(w.x,w.y,1)
            if zl==zl: tgt=min(tgt,zl-0.03)
        if -304.8<w.x<-298.6:
            s=(w.y-yN(w.x))*nrm[1]  # distance S of strip N edge
            if 1.45<=s<2.65: tgt=max(tgt,zt(w.x)-0.03-0.04*(s-1.45))
            elif 0<=s<1.45: tgt=min(tgt,zt(w.x)-0.10)
        if abs(w.z-tgt)>0.005: w.z=tgt; v.co=inv@w; n+=1
    o.data.update()
print('LAWN170b verts moved',n,'strip x',XS[0],XS[-1],'ztop',round(zt(-304.6),2),round(zt(-298.8),2),flush=True)

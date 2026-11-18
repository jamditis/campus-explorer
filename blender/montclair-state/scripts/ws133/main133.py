# ws133: UNIFY #41 Russ Hall residuals.
# (1) E side: wide concrete walk along the E wing (LiDAR 2023 class-2 intensity: paving s 25..31.6 from the wall, pocket of low
#     intensity at t -2..2.5 = planting bed; apron E toward the low Freeman/dining link roof at s>=36), OSM diagonal walk faces retired.
# (2) Lawn tone: ground faces in a ring around Russ switched from the smeared 2020-ortho drape (roof/shadow colours) to lawn.
# (3) Wing windows hidden behind / cut by the one-storey addition roofs removed.
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/'
P=np.load(D+'ws132/las132.npy'); G2=P[P[:,3]==2]
c=math.hypot(1,0.24); U=np.array([1,-0.24])/c; V=np.array([0.24,1])/c; O=np.array([-150.,-242.])
def W(s,t,z): p=O+s*U+t*V; return Vector((float(p[0]),float(p[1]),float(z)))
def ST(x,y): d=np.array([x,y])-O; return float(d@U),float(d@V)
gs=(G2[:,:2]-O)@np.c_[U,V]; GZ=G2[:,2]
def gz(s,t,r=1.6):
    d2=(gs[:,0]-s)**2+(gs[:,1]-t)**2; m=d2<r*r
    if m.sum()<4: m=d2<(2.5*r)**2
    w=1/(0.3+d2[m]); return float((GZ[m]*w).sum()/w.sum())
col=bpy.data.collections.get('WS133_Russ_E_side') or bpy.data.collections.new('WS133_Russ_E_side')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS133_')]: bpy.data.objects.remove(o)
pc=bpy.data.materials.get('WS3_Concrete_panels_sawcut') or bpy.data.materials['Paving_concrete']
mb=bpy.data.objects['WS131_E_building_W_foot_mulch_bed_tree0001_UNVERIFIED'].data.materials[0]
lawn=bpy.data.materials['COLE_lawn_post2020_bs']
# ---- regions in the building frame ----
WALL=24.95   # E wing wall line (roof outline 25.5 - 0.6 eave + 0.05 band)
walk=[(WALL,31.6,-15.5,13.0),(31.6,34.6,-2.6,2.6)]          # rectangles s0,s1,t0,t1
bed=(WALL,27.6,-2.2,2.6)
def in_rect(s,t,r,e=0.0): return r[0]-e<=s<=r[1]+e and r[2]-e<=t<=r[3]+e
def on_walk(s,t,e=0.0): return any(in_rect(s,t,r,e) for r in walk) and not in_rect(s,t,bed,-e if e>0 else 0)
# ---- walk surface: 0.5 m grid, smoothed LiDAR ground + 2 cm ----
STEP=0.5
def grid_mesh(name,mat,test,zoff,skirt=0.25):
    bm=bmesh.new(); vid={}
    S=np.arange(WALL,34.6+1e-6,STEP); T=np.arange(-15.5,13.0+1e-6,STEP)
    zcache={}
    def zz(i,j):
        if (i,j) not in zcache: zcache[(i,j)]=gz(S[i],T[j])
        return zcache[(i,j)]
    def v(i,j):
        if (i,j) not in vid: vid[(i,j)]=bm.verts.new(W(S[i],T[j],zz(i,j)+zoff))
        return vid[(i,j)]
    for i in range(len(S)-1):
        for j in range(len(T)-1):
            cs,ct=(S[i]+S[i+1])/2,(T[j]+T[j+1])/2
            if test(cs,ct): bm.faces.new((v(i,j),v(i+1,j),v(i+1,j+1),v(i,j+1)))
    # smooth z (no wobble) a few passes, keep plane-ish
    for _ in range(4):
        nz={}
        for vv in bm.verts:
            nb=[e.other_vert(vv).co.z for e in vv.link_edges]
            nz[vv]=0.5*vv.co.z+0.5*sum(nb)/len(nb)
        for vv,z in nz.items(): vv.co.z=z
    # skirt on boundary edges
    bnd=[e for e in bm.edges if e.is_boundary]
    low={}
    for e in bnd:
        for vv in e.verts:
            if vv not in low: low[vv]=bm.verts.new((vv.co.x,vv.co.y,vv.co.z-skirt))
    for e in bnd:
        a,b=e.verts; bm.faces.new((a,b,low[b],low[a]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
ow=grid_mesh('WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints',pc,lambda s,t:on_walk(s,t),0.03)
ob=grid_mesh('WS133_Russ_E_wall_foot_bed_mulch_LiDAR2023lowint_UNVERIFIED',mb,lambda s,t:in_rect(s,t,bed) and s>WALL,-0.04,0.12)
# bed edging: the walk skirt already gives a 7 cm step down into the bed
print('WALK faces',len(ow.data.polygons),'BED faces',len(ob.data.polygons))
# ---- retire Footpaths_OSM faces on/near the new walk and the diagonal OSM walk E of Russ ----
fo=bpy.data.objects['Footpaths_OSM']; me=fo.data; mw=fo.matrix_world
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
kill=[]
for f in bm.faces:
    cc=mw@f.calc_center_median(); s,t=ST(cc.x,cc.y)
    if on_walk(s,t,0.4) or in_rect(s,t,bed,0.2) or (WALL<s<36 and -16<t<12.5): kill.append(f)
bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(me); bm.free(); me.update(); print('OSM faces retired',len(kill))
# ---- proxy for the ground-hold GN ----
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px:
    bm=bmesh.new(); bm.from_mesh(px.data); pm=px.matrix_world.inverted()
    for src in (ow,ob):
        for p in src.data.polygons:
            if p.normal.z>0.7:
                bm.faces.new([bm.verts.new(pm@(src.matrix_world@src.data.vertices[i].co)) for i in p.vertices])
    bm.to_mesh(px.data); bm.free(); px.data.update(); print('proxy faces',len(px.data.polygons))
# ---- lawn tone ring around Russ (ground objects only) ----
def in_bldg(s,t):
    R=[(-17,19,-7.25,7.3),(-23.8,-10.3,-11.55,11.8),(12,25.5,-11.65,11.75),(-31,-23,-6.1,6.6),(-23,-11.5,-14.5,-11),(13,24.1,-14.6,-11)]
    return any(r[0]<=s<=r[1] and r[2]<=t<=r[3] for r in R)
def ring(s,t):
    # around the building, S to the drive (t>-16.5), N to the quad walk (t<16), W to Chapin lot end (s>-36), E to s 36
    return -36<s<36 and -16.5<t<16 and not in_bldg(s,t)
for gn in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill_DTM1m_UNVERIFIEDgrade','WS114_terrain_fan_fill_S_edge_DTM1m_UNVERIFIEDgrade','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED'):
    g=bpy.data.objects.get(gn)
    if not g: continue
    me=g.data; mats=[m.name if m else None for m in me.materials]
    if lawn.name not in mats: me.materials.append(lawn); mats.append(lawn.name)
    li=mats.index(lawn.name); gm=g.matrix_world; n=0
    for p in me.polygons:
        cc=gm@p.center
        if -185<cc.x<-105 and -275<cc.y<-205:
            s,t=ST(cc.x,cc.y)
            if ring(s,t) and p.material_index!=li and (mats[p.material_index] or '').startswith(('Ground_ortho','Lawn_Varied')):
                p.material_index=li; n+=1
    print('LAWN',gn,n)
# ---- windows behind the one-storey additions ----
lows=[(-31.0,-23.0,-6.1,6.6),(-23.0,-11.5,-14.5,-11.0),(13.0,24.1,-14.6,-11.0)]
PAR=130.58
for on in ('WS132_Russ_Hall_window_trim_white_and_sills_UNVERIFIEDrhythm','WS132_Russ_Hall_window_glass_dark_UNVERIFIEDrhythm'):
    o=bpy.data.objects[on]; bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    seen=set(); kill=[]
    for f in bm.faces:
        if f in seen: continue
        isl=[]; stack=[f]; seen.add(f)
        while stack:
            g=stack.pop(); isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h not in seen: seen.add(h); stack.append(h)
        vs={v for g in isl for v in g.verts}
        zs=[v.co.z for v in vs]; cx=sum(v.co.x for v in vs)/len(vs); cy=sum(v.co.y for v in vs)/len(vs); zc=(min(zs)+max(zs))/2
        s,t=ST(cx,cy)
        own=any(abs(zc-q)<0.1 for q in (126.35,129.0,125.35,128.0))
        hit=any(r[0]-0.5<=s<=r[1]+0.5 and r[2]-0.5<=t<=r[3]+0.5 for r in lows)
        if hit and min(zs)<PAR+0.25 and not own: kill+=isl
    # sills sit 0.16 below the window -> same island test catches them separately; also kill sills just under killed panes
    bmesh.ops.delete(bm,geom=list(set(kill)),context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update(); print('WIN removed',on,len(set(kill)))
print('M133 done')
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

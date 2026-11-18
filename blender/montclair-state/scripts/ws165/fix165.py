# ws165: (1) UNIFY #69 — aisle-mouth bed front (S) edge at the Normal Ave W N walk: the WS164 mulch sat flat at walk+0.10 and
#   overlapped the walk 5 cm with no riser -> a lawn sliver showed under it. Design (standard bed-at-walk detail, UNVERIFIED section):
#   the bed's W/N curb (ortho 2020) ends at the walk; there is no curb along the walk, so the mulch is graded DOWN to 2 cm under the
#   walk top over the front 0.8 m and stops at the walk back edge; curb top ramps to walk+0.02 over its last 0.6 m; a short vertical
#   mulch face closes the front; curb inner face added (mulch -> curb top).
# (2) the ~18 m deciduous tree over the bed from the 2023 LiDAR class-1 crown (peak 18.4 m at (-297.1,-239.1); crown h>8 m centroid
#   (-298.4,-243.5); main crown x -304..-292, y -248..-230; returns 5th pct 4 m above ground within r 6 m -> lowest limbs ~3.5-4 m).
#   Trunk placed at (-298.4,-241.0) (between peak and centroid; trunk itself not resolved by LiDAR). Species UNVERIFIED -> campus
#   red-maple asset (T_RedMaple_L1_0004, as ws139), crown raised to 3.5 m.
import bpy, bmesh, math, numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164a.py').read().split('def ramp')[0].split('OB=bpy.data.objects',1)[1])  # dz()
SL=0.236; dv=np.array([-1.0,SL]); dv/=np.linalg.norm(dv); nv=np.array([SL,1.0]); nv/=np.linalg.norm(nv); A0=np.array([-268.8,-262.9])
def npt(x): t=(A0[0]-x)/(-dv[0]); return A0+dv*t
def wb(x): return (npt(x)+nv*(0.18+3.2))[1]
def bvh(objs):
    V=[];F=[]
    for o in objs:
        b=len(V); V+=[o.matrix_world@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
def hz(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
walk=OB['WS163_NormalAve_W_N_sidewalk_3p2m_LiDAR2023_int_UNVERIFIED']; TW=bvh([walk])
def wz(x):
    z=hz(TW,x,wb(x)-0.15); return z
def fdist(x,y):  # distance N of the walk back edge (perpendicular)
    p=npt(x); return float(np.dot(np.array([x,y])-(npt(x)+nv*(0.18+3.2)),nv))
mul=OB['WS164_aisle_mouth_mulch_bed_ortho2020_LiDAR2023_flat']; cur=OB['WS164_aisle_mouth_bed_curb_ortho2020_UNVERIFIEDsection']
# --- mulch: cut lines parallel to the walk, then regrade
me=mul.data; bm=bmesh.new(); bm.from_mesh(me); mw=mul.matrix_world
base=npt(-300.0)+nv*(0.18+3.2)
for off in (0.0,0.2,0.4,0.6,0.8):
    co=Vector((base[0]+nv[0]*off, base[1]+nv[1]*off, 0)); geom=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=geom,plane_co=mw.inverted()@co,plane_no=Vector((nv[0],nv[1],0)))
# delete the part S of the walk back edge (the 5 cm overlap)
kill=[f for f in bm.faces if fdist(*(mw@f.calc_center_median()).xy)<0]
bmesh.ops.delete(bm,geom=kill,context='FACES')
n=0
for v in bm.verts:
    p=mw@v.co; d=fdist(p.x,p.y); w=wz(min(max(p.x,-305.45),-300.2))
    if w is None: continue
    zf=w-0.02; zb=p.z; t=min(max(d/0.8,0),1); t=t*t*(3-2*t)
    p.z=zf+(zb-zf)*t; v.co=mw.inverted()@p; n+=1
# front vertical face: boundary edges lying on d≈0
fe=[e for e in bm.edges if e.is_boundary and (all(abs(fdist(*(mw@vv.co).xy))<0.02 for vv in e.verts) or all(abs((mw@vv.co).x+300.0)<0.02 for vv in e.verts))]
for e in fe:
    a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12)))
    try: bm.faces.new((a,b,b2,a2))
    except ValueError: pass
bm.to_mesh(me); bm.free(); me.update(); print('MULCH regraded',n,'front edges',len(fe),flush=True)
mul.name='WS165_aisle_mouth_mulch_bed_graded_to_walk_UNIFY69'
# --- curb: ramp top down over last 0.6 m at the walk; inner face
me=cur.data; mw=cur.matrix_world; mi=mw.inverted(); TM=bvh([mul]); nc=0
for v in me.vertices:
    p=mw@v.co; d=fdist(p.x,p.y)
    if d<0.6:
        w=wz(min(max(p.x,-305.45),-300.2))
        if w is None: continue
        top=p.z if True else 0
        # top verts are those above walk+0.05; bottom verts were top-0.30
        t=min(max(d/0.6,0),1)
        if p.z>w+0.0: 
            zt=w+0.02+(p.z-(w+0.02))*t
            if p.z-zt>0: p.z=zt; v.co=mi@p; nc+=1
me.update()
bm=bmesh.new(); bm.from_mesh(me)
# inner face: for each top-band face, its inner edge (verts with min dist to mulch) -> drop to mulch
added=0
inner=[v for v in bm.verts if hz(TM,*(mw@v.co).xy) is not None and (mw@v.co).z>hz(TM,*(mw@v.co).xy)+0.01]
iv={v.index for v in inner}
for e in list(bm.edges):
    a,b=e.verts
    if a.index in iv and b.index in iv and len(e.link_faces)==1:
        pa=mw@a.co; pb=mw@b.co; za=hz(TM,pa.x,pa.y); zb=hz(TM,pb.x,pb.y)
        a2=bm.verts.new(mi@Vector((pa.x,pa.y,za-0.03))); b2=bm.verts.new(mi@Vector((pb.x,pb.y,zb-0.03)))
        try: bm.faces.new((a,b,b2,a2)); added+=1
        except ValueError: pass
bm.to_mesh(me); bm.free(); me.update(); print('CURB ramped',nc,'inner faces',added,flush=True)
cur.name='WS165_aisle_mouth_bed_curb_ramped_at_walk_UNIFY69'
# --- ground under the bed front: keep >=6 cm below mulch/curb, but never above the walk
pa=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; gp=OB['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']
TB=bvh([cur,mul]); pc=0
for g in (pa,gp):
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (-306.2<p.x<-299.6 and wb(-300)-1.5<p.y<-248.0): continue
        z=hz(TB,p.x,p.y)
        if z is not None and p.z>z-0.06: p.z=z-0.06; v.co=mi@p; pc+=1
    g.data.update()
print('ground pushed',pc,flush=True)

# --- (3) concrete spur N from the walk along the bed's E edge: 2020 ortho light strip x -300.0..-298.6, walk back edge -> y -247.6,
#   square N end; LiDAR 2023 class-2 intensity bright there. Function UNVERIFIED (pad/stub walk); section 10 cm slab, top flush with the
#   walk at the joint, then ground+3 cm.
for o in [o for o in OB if o.name.startswith('WS165_concrete_spur')]: OB.remove(o)
SX0,SX1,SYN=-300.0,-298.6,-247.6
bm=bmesh.new(); rows=[]
ys=list(np.arange(wb(SX0)-0.0,SYN,0.4))+[SYN]
for y in ys:
    r=[]
    for x in (SX0,(SX0+SX1)/2,SX1):
        yy=max(y,wb(x)) if y==ys[0] else y
        if y==ys[0]: yy=wb(x)
        w=wz(min(x,-300.2)) if wz(x) is None else wz(x)
        d=fdist(x,yy); t=min(max(d/1.2,0),1)
        z=(w+0.0)*(1-t)+(dz(x,yy)+0.03)*t
        r.append(bm.verts.new((x,yy,z)))
    rows.append(r)
for a,b in zip(rows[:-1],rows[1:]):
    for i in range(2): bm.faces.new((a[i],a[i+1],b[i+1],b[i]))
# skirts on E, W, N
def sk(vs):
    for p,q in zip(vs[:-1],vs[1:]):
        p2=bm.verts.new(p.co-Vector((0,0,0.15))); q2=bm.verts.new(q.co-Vector((0,0,0.15)))
        bm.faces.new((p,q,q2,p2))
sk([r[0] for r in rows]); sk([r[2] for r in rows][::-1]); sk(rows[-1][::-1])
for f in bm.faces:
    f.normal_update()
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
zw0=rows[0][1].co.z; zn0=rows[-1][1].co.z
wm=walk.active_material
me=bpy.data.meshes.new('WS165_concrete_spur'); bm.to_mesh(me); bm.free(); me.materials.append(wm)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.5,p.y*0.5)
sp=OB.new('WS165_concrete_spur_N_of_walk_ortho2020_UNVERIFIEDfunction',me); (bpy.data.collections.get('WS163_NormalAve_W_LotS') or bpy.context.scene.collection).objects.link(sp)
TS=bvh([sp]); pc=0
for g in (pa,gp):
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (SX0-0.6<p.x<SX1+0.6 and wb(-299)-0.5<p.y<SYN+0.6): continue
        z=hz(TS,p.x,p.y)
        if z is not None and p.z>z-0.05: p.z=z-0.05; v.co=mi@p; pc+=1
    g.data.update()
print('SPUR faces',len(me.polygons),'ground pushed',pc,'z walk',round(zw0,2),'z N',round(zn0,2),flush=True)
t2=OB.get('WS163_skirt_target_hidden')
if t2:
    tb=bmesh.new(); tb.from_mesh(t2.data); L=tb.verts.layers.float.get('wv_in')
    for o in (sp,):
        for p in o.data.polygons:
            if p.normal.z<0.5: continue
            vs_=[tb.verts.new(o.matrix_world@o.data.vertices[i].co) for i in p.vertices]
            if L:
                for v in vs_: v[L]=0.45
            try: tb.faces.new(vs_)
            except ValueError: pass
    tb.to_mesh(t2.data); tb.free(); t2.data.update(); print('skirt target +spur',flush=True)
# --- tree
for o in [o for o in OB if o.name.startswith('WS165_tree')]: OB.remove(o)
src=OB.get('T_RedMaple_L1_0004')
if src:
    X,Y,H,RZ,CB=-298.4,-241.0,18.0,2.6,3.5
    bb=[src.matrix_world@Vector(c) for c in src.bound_box]; sh=max(c.z for c in bb)-min(c.z for c in bb); k=H/sh
    cx=sum(c.x for c in bb)/8; cy=sum(c.y for c in bb)/8; mz=min(c.z for c in bb)
    t=src.copy(); t.data=src.data.copy(); t.name='WS165_tree_aisle_mouth_LiDAR2023_h18m_RedMaple_UNVERIFIEDspecies'
    for c in list(t.users_collection): c.objects.unlink(t)
    col=bpy.data.collections.get('WS163_NormalAve_W_LotS') or bpy.context.scene.collection; col.objects.link(t)
    w=max(max(c.x for c in bb)-min(c.x for c in bb),max(c.y for c in bb)-min(c.y for c in bb)); KXY=min(1.0,15.0/(w*k))  # LiDAR main crown ~14-15 m across
    ctr=Vector((cx,cy,mz))
    Mw=Matrix.Translation(Vector((X,Y,dz(X,Y)-0.15)))@Matrix.Rotation(RZ,4,'Z')@Matrix.Diagonal((k*KXY,k*KXY,k,1.0))@Matrix.Translation(-ctr)@src.matrix_world
    t.parent=None; t.matrix_world=Mw; bpy.context.view_layer.update()
    print('SRC parent',src.parent.name if src.parent else None,'scale',tuple(round(a,3) for a in src.matrix_world.to_scale()),'sh',round(sh,2),flush=True)
    # crown raise in local space: world clearance CB -> local
    me=t.data; leaf={i for i,s in enumerate(t.material_slots) if s.material and 'Leaf' in s.material.name}
    sc=t.matrix_world.to_scale().z; lz0=min(v.co.z for v in me.vertices); thr=lz0+CB/sc
    bm=bmesh.new(); bm.from_mesh(me)
    kl=[f for f in bm.faces if f.material_index in leaf and f.calc_center_median().z<thr]
    rr=0.8/sc
    kb=[f for f in bm.faces if f.material_index not in leaf and f.calc_center_median().z<thr and (f.calc_center_median().xy-Vector((0,0))).length>rr]
    bmesh.ops.delete(bm,geom=list(set(kl+kb)),context='FACES'); bm.to_mesh(me); bm.free(); me.update()
    lv=[f.calc_center_median().z for f in t.data.polygons] if False else None
    LZ=[ (t.matrix_world@me.vertices[p.vertices[0]].co).z-dz(X,Y) for p in me.polygons if p.material_index in leaf]
    print('LEAF mats',[s.material.name for s in t.material_slots if s.material],'lowest leaf above ground',round(min(LZ),2) if LZ else None,'KXY',round(KXY,3))
    bpy.context.view_layer.update()
    wb_=[t.matrix_world@Vector(c) for c in t.bound_box]
    print('TREE',t.name,'k',round(k,3),'loc',tuple(round(a,2) for a in t.location),'bbox x',round(min(c.x for c in wb_),1),round(max(c.x for c in wb_),1),'y',round(min(c.y for c in wb_),1),round(max(c.y for c in wb_),1),'ztop-g',round(max(c.z for c in wb_)-dz(X,Y),1),'del',len(kl),len(kb),flush=True)
else: print('NO TREE SRC')

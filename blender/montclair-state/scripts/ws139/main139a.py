# ws139: UNIFY #46 (crease/wedge/trees S of the Russ S lot) + #45 residual (walk N-end drape, bank edge)
import bpy, bmesh, os, math, numpy as np
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
W='/workspace/nj-scenes/montclair-state/scripts/'
ZS=np.load(W+'ws138/dtm138_s.npy').astype(float); X0,Y1,R=-185.0,-240.0,4.0
def dz(x,y):
    fi=(x-X0)*R-0.5; fj=(Y1-y)*R-0.5
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
OB=bpy.data.objects
def get(p): return [o for o in OB if o.name.startswith(p)]
col=bpy.data.collections['WS138_Russ_S_lot']
# ---- 1. #46 crease: one common DTM surface for the three ground meshes S/W of the lot
lot=get('WS138a_Russ_S_and_BK_lot')[0]
cv=[];cf=[]
for o in [lot]+get('WS138a_lot_S_curb')+get('WS138a_lot_W_curb')+get('WS138a_lot_E_curb'):
    b=len(cv); cv+= [o.matrix_world@v.co for v in o.data.vertices]; cf+=[[b+i for i in p.vertices] for p in o.data.polygons]
TL=BVHTree.FromPolygons(cv,cf)
BX=(-176.0,-86.5,-302.0,-262.0); FE=2.0
def wbox(x,y):
    d=min(x-BX[0],BX[1]-x,y-BX[2],BX[3]-y)
    return 0 if d<=0 else min(1.0,d/FE)
def covered(x,y):
    for dx,dy in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
        if TL.ray_cast(Vector((x+dx,y+dy,200)),Vector((0,0,-1)))[0] is not None: return True
    return False
tot=0
for o in get('WS110_ground_patch_S_of_y-238')+get('WS133b_ground_patch_Russ_S_E')+get('WS138b_ground_fill'):
    mw=o.matrix_world; mi=mw.inverted(); n=0
    for v in o.data.vertices:
        p=mw@v.co; w=wbox(p.x,p.y)
        if w<=0 or covered(p.x,p.y): continue
        z=dz(p.x,p.y)-0.01; nz=p.z+(z-p.z)*w
        if abs(nz-p.z)>0.002: v.co=mi@Vector((p.x,p.y,nz)); n+=1
    o.data.update(); tot+=n; print('CREASE',o.name[:40],n)
# ---- 2. pale wedge W of the lot: ortho-drape faces -> lawn (2020 ortho: grass under trees)
o=get('WS133b_ground_patch_Russ_S_E')[0]; mats=[m.name for m in o.data.materials]
li=mats.index('COLE_lawn_post2020_bs'); oi=mats.index('Ground_ortho_grass'); n=0
for p in o.data.polygons:
    c=o.matrix_world@p.center
    if p.material_index==oi and -176<c.x<-160 and -290<c.y<-262 and not covered(c.x,c.y): p.material_index=li; n+=1
print('WEDGE faces->lawn',n)
# ---- 3. trees from the 2023 LiDAR canopy peaks (scripts/ws139/trees139.json), copies of campus LiDAR-asset trees
for t in get('WS139_tree_'): OB.remove(t)
tcol=bpy.data.collections.get('WS139_Russ_S_strip_trees') or bpy.data.collections.new('WS139_Russ_S_strip_trees')
if tcol.name not in [c.name for c in col.children]: col.children.link(tcol)
PL=[('A',-163.5,-284.5,11.7,'T_SugarMaple_L1_0000',0.0),('B',-157.5,-281.5,9.5,'T_PinOak_L1_0003',1.1),
    ('C',-142.0,-277.0,20.0,'T_RedMaple_L1_0004',2.0),('D',-140.5,-281.8,21.2,'T_PinOak_L1_0005',3.4),
    ('E',-135.5,-279.3,21.2,'T_SugarMaple_L1_0007',4.4),('F',-120.5,-287.5,19.3,'T_PinOak_L1_0005',5.0),('G',-100.5,-290.5,21.6,'T_RedMaple_L1_0004',0.7)]
for tag,x,y,h,src,rz in PL:
    s=OB[src]; bb=[s.matrix_world@Vector(c) for c in s.bound_box]
    sh=max(c.z for c in bb)-min(c.z for c in bb); k=h/sh
    cx=sum(c.x for c in bb)/8; cy=sum(c.y for c in bb)/8; mz=min(c.z for c in bb)
    t=s.copy(); t.name='WS139_tree_%s_%s_LiDAR2023_h%.0fm_UNVERIFIEDspecies'%(tag,src.split('_')[1],h)
    for c in t.users_collection: c.objects.unlink(t)
    tcol.objects.link(t)
    t.scale=s.scale*k; t.rotation_euler.z=s.rotation_euler.z+rz
    # recompute offset with new rotation
    off=Vector((cx-s.location.x,cy-s.location.y,mz-s.location.z))
    from mathutils import Matrix
    off=Matrix.Rotation(rz,3,'Z')@off*k
    g=dz(x,y)-0.15
    t.location=Vector((x,y,g))-off
    print('TREE',t.name,round(k,3),tuple(round(a,2) for a in t.location))
# ---- 4. #45 residual: old Footpaths_OSM pieces overlapping the WS136a walk N end -> removed, bridge slab
fp=OB['Footpaths_OSM']; mw=fp.matrix_world
bm=bmesh.new(); bm.from_mesh(fp.data); bm.faces.ensure_lookup_table()
dl=[f for f in bm.faces if (lambda c:(-73<c.x<-69 and -203.6<c.y<-199.0))(mw@f.calc_center_median())]
print('FP removed',len(dl),[f.index for f in dl])
bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(fp.data); bm.free(); fp.data.update()
# remaining old-walk verts near y -199 give the N tie-in height
zs=[ (mw@v.co).z for v in fp.data.vertices if -72.5<(mw@v.co).x<-69.5 and -199.4<(mw@v.co).y<-198.6]
zn=(sum(zs)/len(zs)) if zs else 126.66
wk=get('WS136a_Skyline_W_walk_N_of_-248')[0]; wm=wk.matrix_world
tops=[wm@v.co for v in wk.data.vertices]
ntop=[p for p in tops if p.y>-203.15]; zsS=max(p.z for p in ntop) if ntop else 126.22
xw=min(p.x for p in ntop); xe=max(p.x for p in ntop)
print('BRIDGE zS',round(zsS,3),'zN',round(zn,3),'x',round(xw,2),round(xe,2),len(zs))
for b in get('WS139_walk_N_bridge'): OB.remove(b)
bm=bmesh.new(); NY=8; NX=4; ys=np.linspace(-203.1,-198.9,NY+1); xs=np.linspace(xw,xe,NX+1); V={}
def zf(y): t=(y+203.1)/4.2; t=t*t*(3-2*t); return zsS+(zn-0.01-zsS)*t
for i,y in enumerate(ys):
    for j,x in enumerate(xs): V[i,j]=bm.verts.new((x,y,zf(y)))
for i in range(NY):
    for j in range(NX): bm.faces.new((V[i,j],V[i,j+1],V[i+1,j+1],V[i+1,j]))
for j_ in (0,NX):
    for i in range(NY):
        a=V[i,j_];b=V[i+1,j_]; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12)))
        bm.faces.new((a,b,b2,a2))
for f in bm.faces:
    f.normal_update()
me=bpy.data.meshes.new('WS139_walk_N_bridge_to_old_walk_y-203_-199_UNVERIFIEDjoint'); bm.to_mesh(me); bm.free()
me.materials.append(wk.data.materials[0]); uvl=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x*0.25,p.y*0.25)
bo=OB.new(me.name,me); wk.users_collection[0].objects.link(bo)
# ---- 5. #45 skirt above the bank: lift lawn within 1.2 m of the walk edge up to walk top -3 cm (only lift)
edge=[p for p in tops if p.y<-203.0]
kd=kdtree.KDTree(len(edge))
for i,p in enumerate(edge): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
for o in get('WS134_ground')+get('WS133b_ground'):
    mw2=o.matrix_world; mi=mw2.inverted(); n=0
    for v in o.data.vertices:
        p=mw2@v.co
        if not (-75.5<p.x<-67 and -249<p.y<-202.5): continue
        co,i,d=kd.find(Vector((p.x,p.y,0)))
        if d>1.2: continue
        tz=max(edge[i].z for _ in [0])
        # top z near: highest walk vert within 0.6 m
        near=[edge[j].z for (_,j,_) in kd.find_range(Vector((p.x,p.y,0)),0.6)]
        tz=max(near)-0.03 if near else edge[i].z-0.03
        if p.z<tz:
            w=1-max(0,(d-0.3))/0.9; nz=p.z+(tz-p.z)*max(0,min(1,w))
            v.co=mi@Vector((p.x,p.y,nz)); n+=1
    o.data.update(); print('BANK lift',o.name[:40],n)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

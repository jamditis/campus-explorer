# ws134d: UNIFY #42 (walk lift via BVH, Terrain corner-fan + WS60 apron removal, NE crumple) + DAY 18 layer 1 (ground):
# 1 m 2023-DTM ground patch for the Freeman/dining block where no fine ground exists, + Balance Kitchen (Freeman dining
# hall, OSM way 312845862) massing from 2023 LiDAR class 6.
import bpy, bmesh, os, math, json, numpy as np, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/ws134/'
Z=np.load(D+'dtm134.npy'); ZX0,ZY0,_=np.load(D+'dtm134_xy.npy'); C=np.load(D+'cls134.npy')
# fill nan by nearest
nan=np.isnan(Z)
if nan.any():
    jj,ii=np.nonzero(~nan); vals=Z[~nan]
    for j,i in zip(*np.nonzero(nan)):
        k=np.argmin((jj-j)**2+(ii-i)**2); Z[j,i]=vals[k]
def dtm(x,y):
    fx=(x-ZX0); fy=(y-ZY0); i=int(min(max(math.floor(fx),0),Z.shape[1]-2)); j=int(min(max(math.floor(fy),0),Z.shape[0]-2))
    tx=fx-i; ty=fy-j
    return float(Z[j,i]*(1-tx)*(1-ty)+Z[j,i+1]*tx*(1-ty)+Z[j+1,i]*(1-tx)*ty+Z[j+1,i+1]*tx*ty)
OSM=json.load(open(D+'osm134.json'))
def pip(poly,x,y):
    ins=False; n=len(poly)
    for k in range(n):
        x1,y1=poly[k]; x2,y2=poly[(k+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: ins=not ins
    return ins
FREEMAN=OSM['312845860'][:-1]; BK=[(a,b+0.3) for a,b in OSM['312845862'][:-1]]
# ---- B: remove Terrain corner-fan faces (hub near (-131.6,-249.4)) and WS60 apron strips in the block
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; me=t.data
hub=[v.index for v in me.vertices if ((mw@v.co).xy-Vector((-131.6,-249.4))).length<0.3]
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
fan=[f for f in bm.faces if any(v.index in hub for v in f.verts) and max(e.calc_length() for e in f.edges)>4.0]
print('TERRAIN hub',hub,'fan faces',len(fan)); bmesh.ops.delete(bm,geom=fan,context='FACES_ONLY'); bm.to_mesh(me); bm.free()
a=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; amw=a.matrix_world; bm=bmesh.new(); bm.from_mesh(a.data)
ap=[f for f in bm.faces if all((amw@v.co).x>=-132 and -300<=(amw@v.co).y<=-190 for v in f.verts)]
print('APRON faces removed',len(ap)); bmesh.ops.delete(bm,geom=ap,context='FACES_ONLY'); bm.to_mesh(a.data); bm.free()
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
def crop_tree(o,X0,X1,Y0,Y1):
    e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world; V=[mw@v.co for v in m.vertices]; F=[]
    for p in m.polygons:
        xs=[V[i].x for i in p.vertices]; ys=[V[i].y for i in p.vertices]
        if max(xs)>=X0 and min(xs)<=X1 and max(ys)>=Y0 and min(ys)<=Y1: F.append(tuple(p.vertices))
    T=None
    if F:
        used=sorted({i for f in F for i in f}); rm={i:k for k,i in enumerate(used)}
        T=BVHTree.FromPolygons([tuple(V[i]) for i in used],[tuple(rm[i] for i in f) for f in F])
    e.to_mesh_clear(); return T,len(F)
# ---- A: lift WS133 walk/bed onto FINE evaluated ground (+3/+1 cm)
w=bpy.data.objects['WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints']; b=bpy.data.objects['WS133_Russ_E_wall_foot_bed_mulch_LiDAR2023lowint_UNVERIFIED']
FINE=('Terrain_LiDAR','WS113_terrain','WS114_terrain','WS133b_')
trees=[]
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(FINE) and not o.hide_render:
        T,n=crop_tree(o,-131,-114.5,-266,-234)
        if T: trees.append((o.name,T)); print('FINE',o.name,n)
def gfine(x,y):
    best=None
    for n,T in trees:
        h=T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
    return best
for o,off in ((w,0.03),(b,0.01)):
    me=o.data; mw=o.matrix_world; n=0; mx=0; byxy={}; big=0
    for v in me.vertices: byxy.setdefault((round(v.co.x,3),round(v.co.y,3)),[]).append(v)
    for key,vs in byxy.items():
        top=max(vs,key=lambda v:v.co.z); p=mw@top.co; g=gfine(p.x,p.y)
        if g is None: continue
        d=g+off-p.z
        if d>0.12: big+=1; continue   # >9 cm above the LiDAR-built walk = ground error, handled by the ground fix, not by humping the walk
        if d>0:
            for v in vs: v.co.z+=d
            n+=1; mx=max(mx,d)
    me.update(); print('LIFT',o.name[:40],n,'of',len(byxy),'max %.3f'%mx,'skipped_big',big)
# ---- D: ground patch where no fine ground / paving exists
COVER=('Terrain_LiDAR','WS113_terrain','WS114_terrain','WS133b_','WS110_','UA_','Curbs')
PAVE=('Roads_OSM','Footpaths_OSM','WS133_Russ_E_walk','WS133_Russ_E_wall_foot')
ctrees=[]
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(COVER) and not o.hide_render:
        T,n=crop_tree(o,-133,-29,-301,-189)
        if T: ctrees.append((o.name,T)); print('COVER',o.name,n)
ptrees=[]
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(PAVE) and not o.hide_render:
        T,n=crop_tree(o,-133,-29,-301,-189)
        if T: ptrees.append((o.name,T)); print('PAVE',o.name,n)
def under_pave(x,y,z):
    lo=z
    for n,T in ptrees:
        h=T.ray_cast(Vector((x,y,z+3)),Vector((0,0,-1)),6.0)
        if h[0] is not None: lo=min(lo,h[0].z-0.06)
    return lo
def covered(x,y,zg):
    for n,T in ctrees:
        h=T.ray_cast(Vector((x,y,zg+3)),Vector((0,0,-1)),6.0)
        if h[0] is not None: return n
    return None
mats=[m.name for m in bpy.data.materials]
LEAF=next((m for m in mats if 'litter' in m.lower() or 'leaf_floor' in m.lower() or 'forest_floor' in m.lower()),None)
print('LEAF material',LEAF)
img=bpy.data.images.load('//data/ws134/ortho134_Natural2020_x-125_-30_y-300_-190_8pxm.jpg',check_existing=True)
om=bpy.data.materials.get('WS134_ortho_Natural2020_drape_8pxm') or bpy.data.materials.new('WS134_ortho_Natural2020_drape_8pxm')
om.use_nodes=True; nt=om.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); bs=nt.nodes.new('ShaderNodeBsdfPrincipled'); tx=nt.nodes.new('ShaderNodeTexImage'); uv=nt.nodes.new('ShaderNodeUVMap')
tx.image=img; uv.uv_map='ortho134'; bs.inputs['Roughness'].default_value=0.88
nt.links.new(uv.outputs['UV'],tx.inputs['Vector']); nt.links.new(tx.outputs['Color'],bs.inputs['Base Color']); nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
X=np.arange(-132,-30+1e-6,1.0); Y=np.arange(-300,-190+1e-6,1.0)
bm=bmesh.new(); vid={}; stats=collections.Counter()
def V(x,y):
    k=(round(x,2),round(y,2))
    if k not in vid: z_=dtm(x,y)-0.03; vid[k]=bm.verts.new((x,y,under_pave(x,y,z_)))
    return vid[k]
for x in X[:-1]:
    for y in Y[:-1]:
        cx,cy=x+0.5,y+0.5
        if pip(FREEMAN,cx,cy): stats['freeman']+=1; continue
        if pip(BK,cx,cy): stats['bk']+=1; continue
        zc=dtm(cx,cy); cv=covered(cx,cy,zc)
        if cv: stats['cov:'+cv[:14]]+=1; continue
        i=int(math.floor(cx-ZX0)); j=int(math.floor(cy-ZY0))
        cl=int(C[j,i]) if 0<=j<C.shape[0] and 0<=i<C.shape[1] else -1
        mi=1 if cl in (1,3) else (2 if (LEAF and cx>-62 and cl in (0,2)) else 0)
        f=bm.faces.new((V(x,y),V(x+1,y),V(x+1,y+1),V(x,y+1))); f.material_index=mi; stats['mat%d'%mi]+=1
print('PATCH',dict(stats))
me=bpy.data.meshes.new('WS134_ground_patch_Freeman_block_DTM2023_1m_lawn_ortho2020_UNVERIFIED'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['COLE_lawn_post2020_bs']); me.materials.append(om)
if LEAF: me.materials.append(bpy.data.materials[LEAF])
uvl=me.uv_layers.new(name='ortho134')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=((p.x+125)/95.0,(p.y+300)/110.0)
col=bpy.data.collections.get('WS134_Freeman_block') or bpy.data.collections.new('WS134_Freeman_block')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS134_')]: bpy.data.objects.remove(o)
po=bpy.data.objects.new(me.name,me); col.objects.link(po)
# ---- E: Balance Kitchen massing (LiDAR roof zones: W wing 129.85, main/E 130.75, S strip 128.75)
def clip(poly,a,b,c):  # keep a*x+b*y+c>=0
    out=[]; n=len(poly)
    for k in range(n):
        P=poly[k]; Q=poly[(k+1)%n]; fp=a*P[0]+b*P[1]+c; fq=a*Q[0]+b*Q[1]+c
        if fp>=0: out.append(P)
        if (fp>=0)!=(fq>=0): t_=fp/(fp-fq); out.append((P[0]+t_*(Q[0]-P[0]),P[1]+t_*(Q[1]-P[1])))
    return out
XS=-95.5; YS=-264.0
zones=[('E_main',clip(BK,1,0,-XS),130.75),('W_wing',clip(clip(BK,-1,0,XS),0,1,-YS),129.85),('S_strip',clip(clip(BK,-1,0,XS),0,-1,YS),128.75)]
wm=bpy.data.materials.get('UY_Freeman_cream_brick_UNVERIFIED')
cand=[m for m in bpy.data.materials if 'Freeman' in m.name and ('brick' in m.name.lower() or 'cream' in m.name.lower())]
print('BRICK cand',[m.name for m in cand][:6])
wm=cand[0] if cand else bpy.data.materials.new('WS134_cream_brick')
rm=bpy.data.materials.get('WS134_roof_membrane_white') or bpy.data.materials.new('WS134_roof_membrane_white')
rm.use_nodes=True; rb=rm.node_tree.nodes.get('Principled BSDF'); rb.inputs['Base Color'].default_value=(0.78,0.78,0.76,1); rb.inputs['Roughness'].default_value=0.7
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
bm=bmesh.new()
for nm,poly,zr in zones:
    if len(poly)<3: continue
    bot=[bm.verts.new((x,y,dtm(x,y)-0.3)) for x,y in poly]; top=[bm.verts.new((x,y,zr)) for x,y in poly]
    n_=len(poly); tf=bm.faces.new(top)
    for k in range(n_):
        f=bm.faces.new((bot[k],bot[(k+1)%n_],top[(k+1)%n_],top[k])); f.material_index=0
    tf.normal_update()
    if tf.normal.z<0: tf.normal_flip()
    r1=bmesh.ops.inset_region(bm,faces=[tf],thickness=0.25,depth=0)
    for f in r1['faces']: f.material_index=2
    r2=bmesh.ops.inset_region(bm,faces=[tf],thickness=0.0,depth=0)
    for f in r2['faces']: f.material_index=0
    for v in tf.verts: v.co.z-=0.35
    tf.material_index=1
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS134_Balance_Kitchen_Freeman_dining_massing_LiDAR2023_OSM312845862_UNVERIFIEDfacade'); bm.to_mesh(me); bm.free()
for m_ in (wm,rm,cm or rm): me.materials.append(m_)
bo=bpy.data.objects.new(me.name,me); col.objects.link(bo)
print('BK zones',[(n,len(p),z) for n,p,z in zones])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

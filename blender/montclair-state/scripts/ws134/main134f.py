# ws134f: UNIFY #42 NE-leg crumple. Box x -132..-105, y -250..-218 (between the WS133 E walk, Freeman SW corner and
# Balance Kitchen W face) was a stack of Terrain fan/seam faces, WS113/WS114 fill faces and the Footpaths_OSM drape at
# different heights. Retire those faces in the box; rebuild as ONE 0.5 m 2023-DTM lawn patch + the NE-leg walk on OSM
# footway 312845863 (A(-117,-233.2) -> B(-112.6,-214.8)), 4.0 m wide (LiDAR 2023 intensity band t -2..+2.3 m and the
# 2020 ortho pale band; UNVERIFIED width/joints), concrete like the WS133 walk.
import bpy, bmesh, os, math, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/ws134/'
exec(open(D+'dtm_helpers.py').read())
BX0,BX1,BY0,BY1=-132.0,-105.0,-250.0,-218.0
def inbox(p): return BX0<=p.x<=BX1 and BY0<=p.y<=BY1
tot={}
for o in list(bpy.data.objects):
    if o.type!='MESH': continue
    if not o.name.startswith(('Terrain_LiDAR','WS113_terrain','WS114_terrain','Footpaths_OSM','WS134_ground_patch')): continue
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    if o.name.startswith('Footpaths_OSM'): dl=[f for f in bm.faces if inbox(mw@f.calc_center_median())]
    else: dl=[f for f in bm.faces if all(inbox(mw@v.co) for v in f.verts)]
    if dl: bmesh.ops.delete(bm,geom=dl,context='FACES_ONLY'); bm.to_mesh(o.data); tot[o.name[:40]]=len(dl)
    bm.free()
print('RETIRED',tot)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def tree_of(names,X0,X1,Y0,Y1):
    out=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render or not o.name.startswith(names): continue
        e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world; V=[mw@v.co for v in m.vertices]; F=[]
        for p in m.polygons:
            xs=[V[i].x for i in p.vertices]; ys=[V[i].y for i in p.vertices]
            if max(xs)>=X0 and min(xs)<=X1 and max(ys)>=Y0 and min(ys)<=Y1: F.append(tuple(p.vertices))
        if F:
            used=sorted({i for f in F for i in f}); rm={i:k for k,i in enumerate(used)}
            out.append((o.name,BVHTree.FromPolygons([tuple(V[i]) for i in used],[tuple(rm[i] for i in f) for f in F])))
        e.to_mesh_clear()
    return out
BLD=tree_of(('WS132_Russ_Hall_walls','WS132_Russ_Hall_hip','WS132_Russ_Hall_water','WS134_Balance','Freeman Hall walls'),BX0,BX1,BY0,BY1)
PAV=tree_of(('WS133_Russ_E_walk','WS133_Russ_E_wall_foot'),BX0,BX1,BY0,BY1)
def hit(trees,x,y,z0=400,dist=1e9):
    for n,T in trees:
        h=T.ray_cast(Vector((x,y,z0)),Vector((0,0,-1)),dist)
        if h[0] is not None: return h[0].z
    return None
OSM=json.load(open(D+'osm134.json'))
FREEMAN=OSM['312845860'][:-1]; BK=[(a,b+0.3) for a,b in OSM['312845862'][:-1]]
A=np.array([-117.0,-233.2]); B=np.array([-112.6,-214.8]); d=(B-A)/np.linalg.norm(B-A); n=np.array([-d[1],d[0]]); L=float(np.linalg.norm(B-A))
TC,HW=0.15,2.0
def on_walk(x,y):
    r=np.array([x,y])-A; s=r@d; t=r@n; return (-1.5<=s<=L+1.2) and abs(t-TC)<=HW
def zg(x,y):
    z=dtm(x,y)-0.03; p=hit(PAV,x,y,z+3,6)
    if p is not None: z=min(z,p-0.06)
    if on_walk(x,y): z=min(z,walk_top(x,y)-0.08)
    return z
def walk_top(x,y):
    # smooth: DTM along the centreline (no cross-wobble) + 1.5 % cross-fall toward W (t<0)
    r=np.array([x,y])-A; s=float(np.clip(r@d,-1.5,L+1.2)); t=r@n
    c=A+d*s+n*TC; return dtm(c[0],c[1])+0.04+0.015*(t-TC)
bm=bmesh.new(); vid={}
def V(x,y):
    k=(round(x,2),round(y,2))
    if k not in vid: vid[k]=bm.verts.new((x,y,zg(x,y)))
    return vid[k]
nf=0
for x in np.arange(BX0,BX1,0.5):
    for y in np.arange(BY0,BY1,0.5):
        cx,cy=x+0.25,y+0.25
        if pip(FREEMAN,cx,cy) or pip(BK,cx,cy): continue
        if hit(BLD,cx,cy) is not None: continue
        bm.faces.new((V(x,y),V(x+0.5,y),V(x+0.5,y+0.5),V(x,y+0.5))); nf+=1
me=bpy.data.meshes.new('WS134f_ground_patch_NE_leg_box_DTM2023_0p5m_lawn_UNVERIFIED'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['COLE_lawn_post2020_bs'])
col=bpy.data.collections['WS134_Freeman_block']
for o in [o for o in bpy.data.objects if o.name.startswith(('WS134f_','WS134g_'))]: bpy.data.objects.remove(o)
col.objects.link(bpy.data.objects.new(me.name,me)); print('BOXPATCH faces',nf)
# walk: 0.5 m stations, 9 cross verts, top + side skirts 0.2 m
w133=bpy.data.objects['WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints']
bm=bmesh.new(); rows=[]
S=list(np.arange(-1.5,L+1.2,0.5))+[L+1.2]
for s in S:
    row=[]
    for t in np.linspace(TC-HW,TC+HW,9):
        p=A+d*s+n*t; row.append(bm.verts.new((p[0],p[1],walk_top(p[0],p[1]))))
    rows.append(row)
for i in range(len(rows)-1):
    for j in range(8): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for j in (0,8):
    sk=[bm.verts.new((r[j].co.x,r[j].co.y,r[j].co.z-0.2)) for r in rows]
    for i in range(len(rows)-1):
        f=bm.faces.new((rows[i][j],rows[i+1][j],sk[i+1],sk[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<-0.5: f.normal_flip()
me=bpy.data.meshes.new('WS134g_NE_leg_walk_concrete_OSM312845863_4m_LiDAR2023int_ortho2020_UNVERIFIEDwidth'); bm.to_mesh(me); bm.free()
for m_ in w133.data.materials: me.materials.append(m_)
# UV like a world-planar map so joint textures run
uvl=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; r=np.array([p.x,p.y])-A; uvl.data[lp.index].uv=(float(r@n)/2.0,float(r@d)/2.0)
col.objects.link(bpy.data.objects.new(me.name,me)); print('WALK stations',len(S),'L %.1f'%L)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

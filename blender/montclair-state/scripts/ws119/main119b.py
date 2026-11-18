# ws119 UNIFY #21: terrace walk continues N along the facade at entrance level (LiDAR 124.8-124.95 hugging the
# wall to y~-170), retained on its W side (LiDAR drop 0.6-1.0 m over <=2 m = wall), and the ground W of the wall
# down to the College Ave table is plaza paving (2020 ortho: continuous pale paving, no lawn), not lawn.
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
def sdtm(x,y): return sum(dtm(x+dx,y+dy) for dx in (-1,0,1) for dy in (-1,0,1))/9
ZL=124.77; Y0=-182.0; Y1=-172.0
xw=lambda y: -211.02+(y-Y0)*(3.12/10.0)          # walk W edge / wall E face (straight, NNE)
zt=lambda y: ZL+0.13*min(1.0,max(0.0,(y-Y0)/5.0)) # walk top: 2.6 % rise then level 124.90
dg=bpy.context.evaluated_depsgraph_get()
def bv(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
B=[bv(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS107_Chapin')]
def xf(y):
    xs=[h[0].x for h in (b.ray_cast(Vector((-215,y,125.6)),Vector((1,0,0)),30) for b in B) if h[0] is not None]
    return min(xs)+0.15
T102=bv(next(o for o in bpy.data.objects if o.name.startswith('WS102_CollegeAve_S_carriageway')))
C102=bv(next(o for o in bpy.data.objects if o.name.startswith('WS102_CollegeAve_S_curb_E')))
CON=bv(next(o for o in bpy.data.objects if o.name.startswith('WS116_Chapin_W_N_connector')))
def zhit(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
def westx(y):  # E boundary of the table / curb along a row
    x=-211.5
    while x>-226:
        if zhit(T102,x,y) is not None or zhit(C102,x,y) is not None: return x+0.02
        x-=0.05
    return -224.0
slab=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_landing'))
wallo=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_cheek'))
pmat=bpy.data.objects[[o.name for o in bpy.data.objects if o.name.startswith('WS116_Chapin_W_plaza_concrete')][0]].data.materials[0]
def newobj(name,mat):
    me=bpy.data.meshes.new(name); ob=bpy.data.objects.new(name,me)
    for c in slab.users_collection: c.objects.link(ob)
    me.materials.append(mat); return ob
def band(ob,ys,xa,xb,za,zb,closed=True):
    bm=bmesh.new(); Rr=[]
    for y in ys:
        x0=xa(y); x1=xb(y); Rr.append([bm.verts.new(c) for c in ((x0,y,za(x0,y)),(x1,y,za(x1,y)),(x1,y,zb(x1,y)),(x0,y,zb(x0,y)))])
    for r0,r1 in zip(Rr[:-1],Rr[1:]):
        for i in range(4):
            j=(i+1)%4; bm.faces.new((r0[i],r0[j],r1[j],r1[i]))
    bm.faces.new(Rr[0][::-1]); bm.faces.new(Rr[-1]); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()
ys=list(np.linspace(Y0,Y1,21))
# 1 terrace walk N
walk=newobj('WS119_Chapin_W_terrace_walk_N_entrance_level_LiDAR2023_UNIFY21_UNVERIFIEDw',slab.data.materials[0])
band(walk,ys,lambda y: xw(y)-0.02,xf,lambda x,y: ZL-1.2,lambda x,y: zt(y))
# 2 retaining wall continues (same section as ws118: 0.30 m, top walk+0.45, footing DTM-0.40), ends square at Y1
wl=newobj('WS119_Chapin_W_terrace_wall_N_continuation_white_UNVERIFIEDheight',wallo.data.materials[0])
band(wl,ys,lambda y: xw(y)-0.30,lambda y: xw(y)+0.01,lambda x,y: min(dtm(x,y),dtm(x-0.5,y))-0.40,lambda x,y: zt(y)+0.45)
# 3 plaza W of the wall, from the table/curb edge to the wall foot, S edge = connector/bed N ends (y -182)
def zp(x,y):
    z=sdtm(x,y)+0.05
    zr=zhit(T102,x-0.3,y) or zhit(C102,x-0.3,y)
    xe=westx(y); d=x-xe
    if zr is not None and d<1.5: z=zr+(z-zr)*(d/1.5)
    if y<Y0+2.0:
        zc=zhit(CON,x,Y0-0.05)
        if zc is not None: z=zc+(z-zc)*((y-Y0)/2.0)
    return z
pz=newobj('WS119_Chapin_W_N_plaza_concrete_ortho2020_DTM2023_UNIFY21_UNVERIFIEDgrade',pmat)
bm=bmesh.new(); NC=14; G=[]
for y in ys:
    xa=westx(y); xb=xw(y)-0.30; G.append([bm.verts.new((xa+(xb-xa)*k/NC,y,0)) for k in range(NC+1)])
for row in G:
    for v in row: v.co.z=zp(v.co.x,v.co.y)
for r0,r1 in zip(G[:-1],G[1:]):
    for k in range(NC): bm.faces.new((r0[k],r0[k+1],r1[k+1],r1[k]))
# thickness skirt so edges don't show a knife edge
ret=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces)); vs=[e for e in ret['geom'] if isinstance(e,bmesh.types.BMVert)]
for v in vs: v.co.z-=0.25
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(pz.data); bm.free()
print('M119b westx',[(round(y,1),round(westx(y),2)) for y in ys[::4]])
# 4 retire Footpaths faces under walk/wall/plaza; push terrain under
def inzone(x,y,m=0.0): return Y0-m<=y<=Y1+m and westx(min(max(y,Y0),Y1))-m<=x<=xf(min(max(y,Y0),Y1))+m
fp=bpy.data.objects['Footpaths_OSM']; b=bmesh.new(); b.from_mesh(fp.data); fw=fp.matrix_world
kill=[f for f in b.faces if (lambda c: Y0+0.05<=c.y<=Y1-0.05 and inzone(c.x,c.y))(fw@f.calc_center_median())]
bmesh.ops.delete(b,geom=kill,context='FACES'); b.to_mesh(fp.data); b.free(); fp.data.update(); print('M119b Footpaths retired',len(kill))
PB=[bv(o) for o in (walk,pz,wl)]
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=next(o for o in bpy.data.objects if o.name.startswith(nm)); mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if Y0-0.8<=w.y<=Y1+0.8 and -226<w.x<-200:
            zs=[zhit(bb,w.x+dx,w.y+dy) for bb in PB for dx in (-0.5,0,0.5) for dy in (-0.5,0,0.5)]
            zs=[z for z in zs if z is not None]
            if zs and w.z>min(zs)-0.08: w.z=min(zs)-0.08; v.co=inv@w; n+=1
    o.data.update(); print('M119b',nm,'pushed',n)
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M119b SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M119b SAVED',SAVE)

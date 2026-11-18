# ws120 UNIFY #24 (plaza N of y -172: paving to y -162 + D-shaped raised planter that takes the remaining
# terrace/plaza grade where the retaining wall ends) and UNIFY #25 (S-wing door apron S of the stair foot).
import bpy, bmesh, numpy as np, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state/'
DT=np.load(R+'data/dtm_1m.npy'); H=DT.shape[0]/2
def dtm(x,y):
    fx=x+H-0.5; fy=y+H-0.5; j=int(np.floor(fx)); i=int(np.floor(fy)); a=fx-j; b=fy-i
    return float(DT[i,j]*(1-a)*(1-b)+DT[i,j+1]*a*(1-b)+DT[i+1,j]*(1-a)*b+DT[i+1,j+1]*a*b)
def sdtm(x,y): return sum(dtm(x+dx,y+dy) for dx in (-1,0,1) for dy in (-1,0,1))/9
dg=bpy.context.evaluated_depsgraph_get()
def bv(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
def ob(prefix): return next(o for o in bpy.data.objects if o.name.startswith(prefix))
def zhit(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
B=[bv(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS107_Chapin')]
def xf(y,z=125.6,x0=-215):
    xs=[h[0].x for h in (b.ray_cast(Vector((x0,y,z)),Vector((1,0,0)),30) for b in B) if h[0] is not None]
    return (min(xs)+0.15) if xs else -201.0
T102=bv(ob('WS102_CollegeAve_S_carriageway')); C102=bv(ob('WS102_CollegeAve_S_curb_E'))
def westx(y):
    x=-209.5
    while x>-226:
        if zhit(T102,x,y) is not None or zhit(C102,x,y) is not None: return x+0.02
        x-=0.05
    return -224.0
P119=ob('WS119_Chapin_W_N_plaza_concrete'); W119=ob('WS119_Chapin_W_terrace_walk_N_entrance')
wallo=ob('WS119_Chapin_W_terrace_wall_N_continuation'); cop=ob('WS119_Chapin_W_terrace_wall_coping')
mulch=ob('WS116_Chapin_W_bed_E2_mulch').data.materials[0]
BS=[bv(P119),bv(W119)]
def newobj(name,mat,like=P119):
    me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me)
    for c in like.users_collection: c.objects.link(o)
    me.materials.append(mat); return o
Y0=-172.0; Y1=-162.0
def zS(x):
    for d in (0,0.15,-0.15,0.3,-0.3,0.45,-0.45):
        zs=[zhit(b,x+d,Y0-0.05) for b in BS]; zs=[z for z in zs if z is not None]
        if zs: return max(zs)
    return None
def zp(x,y):
    z=sdtm(x,y)+0.05
    zr=zhit(T102,x-0.3,y) or zhit(C102,x-0.3,y); d=x-westx(y)
    if zr is not None and d<1.5: z=zr+(z-zr)*(max(d,0)/1.5)
    s=zS(x)
    if s is not None and y<Y0+2.5: z=s+(z-s)*((y-Y0)/2.5)
    return z
# --- 1 plaza N extension
pz=newobj('WS120_Chapin_W_N_plaza_ext_to_y-162_concrete_ortho2020_DTM2023_UNIFY24_UNVERIFIEDgrade',P119.data.materials[0])
ys=list(np.linspace(Y0,Y1,21)); NC=24
bm=bmesh.new(); G=[]
for y in ys:
    xa=westx(y); xb=xf(y)
    G.append([bm.verts.new((xa+(xb-xa)*k/NC,y,0)) for k in range(NC+1)])
for row in G:
    for v in row: v.co.z=zp(v.co.x,v.co.y)
for r0,r1 in zip(G[:-1],G[1:]):
    for k in range(NC): bm.faces.new((r0[k],r0[k+1],r1[k+1],r1[k]))
ret=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces))
for v in [e for e in ret['geom'] if isinstance(e,bmesh.types.BMVert)]: v.co.z-=0.25
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(pz.data); bm.free()
print('M120 ext rows',[(round(y,1),round(westx(y),2),round(xf(y),2)) for y in ys[::5]])
# --- 2 D-shaped raised planter (2020 ortho: dark bed x -211.2..-205.4, y -171..-165.5, flat S side lit white)
CX,CY,AX,BY=-208.3,-171.9,2.95,6.2; TOP=125.20; TW=0.25
def dshape(a,b,n=28):
    pts=[(CX-a,CY)]+[(CX-a*math.cos(t),CY+b*math.sin(t)) for t in np.linspace(0,math.pi,n)[1:-1]]+[(CX+a,CY)]
    return pts
outer=dshape(AX,BY); inner=dshape(AX-TW,BY-TW)
def ring(o,pi,po,ztop,zbot_fn,closed_flat=True):
    bm=bmesh.new(); n=len(po)
    ot=[bm.verts.new((x,y,ztop)) for x,y in po]; it=[bm.verts.new((x,y+ (TW if closed_flat else 0),ztop)) for x,y in pi]
    ob_=[bm.verts.new((x,y,zbot_fn(x,y))) for x,y in po]; ib=[bm.verts.new((x,y+(TW if closed_flat else 0),zbot_fn(x,y))) for x,y in pi]
    loop=list(range(n))
    for i in range(n):
        j=(i+1)%n
        bm.faces.new((ot[i],ot[j],it[j],it[i])); bm.faces.new((ob_[j],ob_[i],ib[i],ib[j]))
        bm.faces.new((ot[j],ot[i],ob_[i],ob_[j])); bm.faces.new((it[i],it[j],ib[j],ib[i]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(o.data); bm.free()
pw=newobj('WS120_Chapin_W_round_planter_D_wall_precast_white_ortho2020_UNIFY24_UNVERIFIEDheight',wallo.data.materials[0])
ring(pw,inner,outer,TOP,lambda x,y: min(dtm(x,y),sdtm(x,y))-0.40)
# mulch fill
pm=newobj('WS120_Chapin_W_round_planter_mulch_UNVERIFIED',mulch)
bm=bmesh.new(); vs=[bm.verts.new((x,y+TW,TOP-0.12)) for x,y in inner]; bm.faces.new(vs)
bmesh.ops.triangulate(bm,faces=bm.faces); bm.to_mesh(pm.data); bm.free()
# shrubs (low evergreen mass) + one small ornamental tree: approximated
shm=bpy.data.materials.new('WS120_planter_shrub_evergreen_solid'); shm.use_nodes=True
bsdf=shm.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value=(0.055,0.13,0.04,1); bsdf.inputs['Roughness'].default_value=0.85
shm.diffuse_color=(0.055,0.13,0.04,1)
print('M120 shrub mat',shm.name)
sh=newobj('WS120_Chapin_W_round_planter_shrubs_UNVERIFIEDspecies',shm)
bm=bmesh.new(); rng=np.random.default_rng(120)
spots=[(-210.3,-171.0),(-208.9,-170.9),(-207.5,-171.0),(-206.3,-170.8),(-209.9,-169.3),(-206.7,-169.2),(-209.3,-167.6),(-207.3,-167.5),(-208.3,-166.5)]
for (x,y) in spots:
    r=0.45+0.15*rng.random()
    g=bmesh.ops.create_icosphere(bm,subdivisions=3,radius=r)
    for v in g['verts']: v.co.z*=0.75; v.co+=Vector((x,y,TOP-0.12+r*0.55))
bm.to_mesh(sh.data); bm.free()
for p in sh.data.polygons: p.use_smooth=True
tr=newobj('WS120_Chapin_W_round_planter_ornamental_tree_UNVERIFIED',shm)
bm=bmesh.new()
g=bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.09,radius2=0.06,depth=2.0)
for v in g['verts']: v.co+=Vector((-208.3,-168.6,TOP-0.12+1.0))
g=bmesh.ops.create_icosphere(bm,subdivisions=3,radius=1.4)
for v in g['verts']: v.co.z*=0.8; v.co+=Vector((-208.3,-168.6,TOP+2.6))
bm.to_mesh(tr.data); bm.free()
bark=next((m for m in bpy.data.materials if 'bark' in m.name.lower()),None)
if bark: tr.data.materials.append(bark); [setattr(p,'material_index',1) for p in tr.data.polygons if p.center.z<TOP+1.6]
for p in tr.data.polygons: p.use_smooth=True
# --- 3 UNIFY #25 S-wing door apron: plaza level E to the S-wing W face, S of the stair
PL=bv(ob('WS116_Chapin_W_plaza_concrete')); COR=bv(ob('WS116_Chapin_W_plaza_E_corridor'))
ya,yb=-203.3,-201.3
fx=[xf(y,123.6,-219.0) for y in np.linspace(ya,yb,5)]
print('M120 S-wing face x',[round(v,2) for v in fx])
zc=zhit(COR,-217.6,-200.3) or zhit(PL,-219.0,-201.5)
ap=newobj('WS120_Chapin_W_S_wing_door_apron_concrete_plaza_level_UNIFY25_UNVERIFIED',P119.data.materials[0])
bm=bmesh.new(); G=[]
for y in np.linspace(ya,yb,5):
    xa=-218.75; xb=xf(y,123.6,-219.0)
    z0=zhit(PL,xa-0.05,y) or zc
    G.append([bm.verts.new((xa+(xb-xa)*k/8,y,z0+(zc-z0)*min(1,k/4)+0.0)) for k in range(9)])
for r0,r1 in zip(G[:-1],G[1:]):
    for k in range(8): bm.faces.new((r0[k],r0[k+1],r1[k+1],r1[k]))
ret=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces))
for v in [e for e in ret['geom'] if isinstance(e,bmesh.types.BMVert)]: v.co.z-=0.25
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(ap.data); bm.free()
print('M120 apron z',round(zc,3))
# --- 4 retire Footpaths faces under the extension/planter, push terrain under
def inzone(x,y): return Y0+0.05<=y<=Y1-0.3 and westx(y)-0.1<=x<=xf(y)+0.2
fp=bpy.data.objects['Footpaths_OSM']; b=bmesh.new(); b.from_mesh(fp.data); fw=fp.matrix_world
kill=[f for f in b.faces if (lambda c: inzone(c.x,c.y) or (ya<=c.y<=yb and -218.8<=c.x<=-212))(fw@f.calc_center_median())]
bmesh.ops.delete(b,geom=kill,context='FACES'); b.to_mesh(fp.data); b.free(); fp.data.update(); print('M120 Footpaths retired',len(kill))
PB=[bv(o) for o in (pz,ap)]
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=ob(nm); mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if (Y0-0.8<=w.y<=Y1+0.8 and -226<w.x<-200) or (ya-1.0<=w.y<=yb+0.5 and -220<w.x<-210):
            zs=[zhit(bb,w.x+dx,w.y+dy) for bb in PB for dx in (-0.5,0,0.5) for dy in (-0.5,0,0.5)]
            zs=[z for z in zs if z is not None]
            if zs and w.z>min(zs)-0.08: w.z=min(zs)-0.08; v.co=inv@w; n+=1
    o.data.update(); print('M120',nm,'pushed',n)
# #25: terrain at the S-wing W face foot S of the stair was DTM interpolated into the building (mound); clamp to apron level
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=ob(nm); mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if -208.5<=w.y<=-201.0 and -219.0<=w.x<=-211.0 and w.z>zc-0.06:
            w.z=zc-0.06; v.co=inv@w; n+=1
    o.data.update(); print('M120 #25 clamp',nm,n)
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M120 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M120 SAVED',SAVE)

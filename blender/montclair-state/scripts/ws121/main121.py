# ws121 UNIFY #26: plaza NW corner. The WS120 plaza N edge (y -162) met a fragmented residue of the Footpaths_OSM
# drape (crumpled triangles x -213..-207, y -162.5..-159.8, partly z-fighting the plaza) = the "pale cracked slab".
# 2020 ortho: the College Ave E sidewalk (verge between it and the curb) flares out SE into the plaza with a curved
# NE edge. Build: one connector slab plaza-N-edge -> walk S end, W edge on the road edge with the verge ending in a
# taper, NE edge a quarter-ellipse flare; retire the residue; push lawn under.
import bpy, bmesh, numpy as np, os, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
def bvo(o):
    mw=o.matrix_world; me=o.data
    return BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def zh(b,x,y):
    h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150); return None if h[0] is None else h[0].z
fp=ob('Footpaths_OSM'); fw=fp.matrix_world
PE=ob('WS120_Chapin_W_N_plaza_ext'); BPE=bvo(PE)
ROADS=[bvo(ob(n)) for n in ('WS102_CollegeAve_S_carriageway','WS27_CollegeAve_carriageway','WS27_CollegeAve_curb_left','WS102_CollegeAve_S_curb_E')]
YS,YN=-162.0,-159.75
# walk extents just N of the cut line
ws=[fw@fp.data.vertices[i].co for p in fp.data.polygons if (lambda c: -159.7<=c.y<=-158.6 and -212.5<=c.x<=-205)(fw@p.center) for i in p.vertices]
WX0=min(v.x for v in ws); WX1=max(v.x for v in ws); print('M121 walk x',round(WX0,2),round(WX1,2))
BFP=bvo(fp)
def roadx(y):
    x=-211.0
    while x>-218:
        if any(zh(b,x,y) is not None for b in ROADS): return x+0.02
        x-=0.05
    return -213.3
def zroad(x,y):
    for b in ROADS:
        z=zh(b,x-0.25,y)
        if z is not None: return z
    return None
# NE flare: quarter ellipse from (WX1,YN) to (XE,YS)
XE=-204.6
def xb(y):
    t=(y-YS)/(YN-YS)  # 0 at S, 1 at N
    return XE+(WX1-XE)*math.sqrt(max(0.0,1-(1-t)**2))
def xa(y):
    yt=-160.6
    if y<=yt: return roadx(y)
    r=roadx(yt); return r+(WX0-r)*((y-yt)/(YN-yt))
def zs_(x):
    for d in (0,0.1,-0.1,0.2):
        z=zh(BPE,x,YS-0.04+d*0)
        if z is not None: return z
    return None
def zn_(x):
    z=zh(BFP,x,YN+0.12)
    if z is None: z=zroad(min(x,WX0),YN)
    return z
NR=10; NC=16
bm=bmesh.new(); G=[]
for i in range(NR+1):
    y=YS+(YN-YS)*i/NR; a=xa(y); b=xb(y); row=[]
    for k in range(NC+1):
        x=a+(b-a)*k/NC
        s=zs_(x); n=zn_(min(max(x,WX0),WX1)) if i>0 else None
        if s is None: s=zs_(-212.6) if x<-212 else zs_(-205.0)
        if n is None: n=s
        t=i/NR; z=s+(n-s)*t
        zr=zroad(x,y) if k==0 else None
        if zr is not None: z=max(zr+0.0,min(z,zr+0.03)) if x<WX0-0.5 else z
        row.append(bm.verts.new((x,y,z)))
    G.append(row)
for r0,r1 in zip(G[:-1],G[1:]):
    for k in range(NC): bm.faces.new((r0[k],r0[k+1],r1[k+1],r1[k]))
ret=bmesh.ops.extrude_face_region(bm,geom=list(bm.faces))
for v in [e for e in ret['geom'] if isinstance(e,bmesh.types.BMVert)]: v.co.z-=0.25
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
nm='WS121_Chapin_W_plaza_NW_corner_sidewalk_flare_concrete_ortho2020_UNIFY26_UNVERIFIEDradius'
me=bpy.data.meshes.new(nm); o=bpy.data.objects.new(nm,me)
for c in PE.users_collection: c.objects.link(o)
print('M121 rows',[(round(r[0].co.y,2),round(r[0].co.x,2),round(r[-1].co.x,2),round(r[0].co.z,3),round(r[NC//2].co.z,3),round(r[-1].co.z,3)) for r in G[::2]])
me.materials.append(PE.data.materials[0]); bm.to_mesh(me); bm.free()
# retire Footpaths residue between the plaza and the walk cut line (and under the plaza ext)
b=bmesh.new(); b.from_mesh(fp.data)
kill=[f for f in b.faces if (lambda c: -163.0<=c.y<=YN and -214.5<=c.x<=-200)(fw@f.calc_center_median())]
bmesh.ops.delete(b,geom=kill,context='FACES'); b.to_mesh(fp.data); b.free(); fp.data.update(); print('M121 Footpaths retired',len(kill))
BN=bvo(o)
for tn in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    t=next((q for q in bpy.data.objects if q.name.startswith(tn)),None)
    if not t: continue
    mw=t.matrix_world; inv=mw.inverted(); n=0
    for v in t.data.vertices:
        w=mw@v.co
        if -163<=w.y<=-159.0 and -215<w.x<-203:
            zz=[zh(BN,w.x+dx,w.y+dy) for dx in (-0.5,0,0.5) for dy in (-0.5,0,0.5)]; zz=[z for z in zz if z is not None]
            if zz and w.z>min(zz)-0.08: w.z=min(zz)-0.08; v.co=inv@w; n+=1
    t.data.update(); print('M121',tn,'pushed',n)
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M121 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M121 SAVED',SAVE)

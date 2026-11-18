"""Session 20261016br (part 2): Cole Hall west portico/arcade + plaza pavilion (the 2020 "new west portico" serving the cafe/Admissions).
Footprints/tops MEASURED from 2023 LiDAR bld cells outside the OSM ring (grid_1m): arcade strip ~2.4 x 23.8 m along the west-wing west
face, top p50 134.95 / max 136.17, ground ~130.35; pavilion ~5 x 5 m at (-180,-72), top p50 134.99 / max 135.79, ground ~130.25.
Form (white arched arcade + red-tile roof; small hip-roofed pavilion with arched openings) from MSU 2020 drone photo (X @MontclairStateU,
eye reference only). Arch splits/pier sizes UNVERIFIED. Idempotent: rebuilds collection COLE_portico_20261016br. SAVE=1 to save."""
import bpy, bmesh, math, os
import numpy as np
from mathutils import Vector, Matrix
ROOT='/workspace/nj-scenes/montclair-state'; COLN='COLE_portico_20261016br'
g=np.load(ROOT+'/north/data/grid_1m.npz'); dtm=g['dtm_filled']
def ground(x,y): return float(dtm[int(math.floor(y+260)),int(math.floor(x+600))])
sc=bpy.context.scene
if COLN in bpy.data.collections:
    c=bpy.data.collections[COLN]
    for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
else:
    c=bpy.data.collections.new(COLN); sc.collection.children.link(c)
M_st=bpy.data.materials['COLE_stucco_plain_bq']; M_roof=bpy.data.materials.get('Roof_tile_or_membrane')
M_dk=bpy.data.materials['COLE_loggia_shadow_bq']; M_br=bpy.data.materials['COLE_dark_brown_wood_bq']
def add_box(bm,cx,cy,z0,z1,hx,hy,rot,mi):
    R=Matrix.Rotation(rot,4,'Z')
    vs=[bm.verts.new(Vector((cx,cy,0))+(R@Vector((sx*hx,sy*hy,0))).to_3d()+Vector((0,0,z))) for z in (z0,z1) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    for f in ((0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bm.faces.new([vs[i] for i in f]).material_index=mi
def arch_run(bm,p0,t,n,L,nb,zg,zs,ztop,pw,th,mi):
    """piers + arched spandrels along a line p0 + t*u (u in 0..L), face normal n. semicircle heads, stepped 14 slices."""
    rr=math.atan2(t.y,t.x); bw=L/nb; r=bw/2-pw/2
    for k in range(nb+1):
        p=p0+t*(k*bw); add_box(bm,p.x,p.y,zg,ztop,pw/2,th/2,rr,mi)
    for k in range(nb):
        xc=(k+0.5)*bw; NS=24
        for j in range(NS):
            xa=-r+2*r*j/NS; xb=-r+2*r*(j+1)/NS; za=zs+math.sqrt(max(0.0,r*r-max(xa*xa,xb*xb)))
            p=p0+t*(xc+(xa+xb)/2); add_box(bm,p.x,p.y,za,ztop,(xb-xa)/2+0.005,th/2,rr,mi)
def new_obj(name,mats):
    me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me); c.objects.link(o)
    for m in mats: me.materials.append(m)
    o['br_source']='20261016br'; return o
# --- arcade: LiDAR min-rect (-161.6,-71.7),(-167.3,-94.8),(-169.7,-94.2),(-163.9,-71.1)
a_in0,a_in1=Vector((-161.6,-71.7)),Vector((-167.3,-94.8)); a_out0=Vector((-163.9,-71.1))
t=(a_in1-a_in0); L=t.length; t/=L; n=(a_out0-a_in0); D=n.length; n/=D      # n points WEST (outward)
a_in0=a_in0-n*0.5; D+=0.5   # inner LiDAR edge sits 0.4-0.6 m off the OSM wall (cell buffer) -> start at the wall
zg=130.35; ZE=134.55; ZW=135.85   # outer eave / roof at wall (LiDAR p50 134.95, p90 135.84, MEASURED; split UNVERIFIED)
arc=new_obj('Cole Hall west portico arcade (LiDAR footprint/top MEASURED; arches UNVERIFIED) br',[M_st,M_roof,M_dk,M_br])
bm=bmesh.new()
# back wall shadow plane (so the arcade reads deep) + floor slab
pm=a_in0+t*(L/2); rr=math.atan2(t.y,t.x)
q=pm+n*(D/2); add_box(bm,q.x,q.y,zg-1.5,zg+0.12,L/2+0.3,D/2+0.3,rr,0)
q=pm+n*(D/2); add_box(bm,q.x,q.y,ZE-0.32,ZE-0.22,L/2,D/2-0.05,rr,3)            # ceiling (dark-brown wood)
nb=max(3,int(round(L/3.3)))
arch_run(bm,a_in0+n*(D-0.3),t,n,L,nb,zg+0.12,zg+0.12+2.2,ZE,0.62,0.6,0)
# entablature band + shed roof (tile) w/ 0.5 m overhang
q=pm+n*(D-0.3); add_box(bm,q.x,q.y,ZE-0.25,ZE,L/2+0.31,0.36,rr,0)
P=lambda u,v,z: (lambda p: Vector((p.x,p.y,z)))(a_in0+t*u+n*v)
top=[P(-0.6,-0.2,ZW),P(L+0.6,-0.2,ZW),P(L+0.6,D+0.5,ZE-0.08),P(-0.6,D+0.5,ZE-0.08)]
vt=[bm.verts.new(p) for p in top]; vb=[bm.verts.new(p-Vector((0,0,0.18))) for p in top]
try:
    bm.faces.new(vt).material_index=1; bm.faces.new(vb[::-1]).material_index=1
    for k in range(4): bm.faces.new([vt[k],vb[k],vb[(k+1)%4],vt[(k+1)%4]]).material_index=1
except ValueError: pass
bm.to_mesh(arc.data); bm.free()
# --- pavilion: LiDAR 5x5 at (-180,-72); hip roof apex 135.79 MEASURED, eave split UNVERIFIED; rotated with the building
rot=math.atan2(-104.247+98.217,-126.347+151.955)
cx,cy=-180.0,-72.0; zgp=130.25; h=2.5; ZEp=134.35; ZA=135.79
pav=new_obj('Cole Hall plaza pavilion (LiDAR footprint/top MEASURED; form UNVERIFIED) br',[M_st,M_roof,M_dk,M_br])
bm=bmesh.new(); Rm=Matrix.Rotation(rot,4,'Z')
add_box(bm,cx,cy,zgp-2.0,zgp+0.15,h+0.25,h+0.25,rot,0)                       # plinth (deep: terrain dips in front)
for s in range(4):
    # side s: run from corner to corner
    corners=[(-h,-h),(h,-h),(h,h),(-h,h)]
    c0=Vector(corners[s]); c1=Vector(corners[(s+1)%4])
    w0=Vector((cx,cy))+(Rm@c0.to_3d()).to_2d(); w1=Vector((cx,cy))+(Rm@c1.to_3d()).to_2d()
    tt=(w1-w0); LL=tt.length; tt/=LL; nn=Vector((tt.y,-tt.x))
    arch_run(bm,w0,tt,nn,LL,1,zgp+0.15,zgp+0.15+1.6,ZEp,0.75,0.5,0)
add_box(bm,cx,cy,ZEp-0.3,ZEp-0.2,h-0.1,h-0.1,rot,3)                              # ceiling
add_box(bm,cx,cy,ZEp-0.22,ZEp,h+0.1,h+0.1,rot,0)                                  # cornice band
b=[bm.verts.new(Vector((cx,cy,ZEp))+(Rm@Vector((sx*(h+0.55),sy*(h+0.55),0))).to_3d()) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
a=bm.verts.new((cx,cy,ZA))
for i in range(4): bm.faces.new([b[i],b[(i+1)%4],a]).material_index=1
bm.faces.new(b[::-1]).material_index=3
bm.to_mesh(pav.data); bm.free()
for o in (arc,pav):
    for p in o.data.polygons: p.use_smooth=False
sc['br_cole_portico']='arcade nb%d L%.1f D%.1f; pavilion 5x5'%(nb,L,D)
print('BR_PORTICO',sc['br_cole_portico'])
def cam(name,loc,tgt,lens):
    o=bpy.data.objects.get(name)
    if not o: o=bpy.data.objects.new(name,bpy.data.cameras.new(name)); sc.collection.objects.link(o)
    o.data.lens=lens; o.data.clip_end=60000; o.location=loc
    o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
cam('CAM_closeup_cole_hall_portico_br',(-194,-64,ground(-194,-64)+2.2),(-168,-83,134.2),30)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('BR_SAVED')

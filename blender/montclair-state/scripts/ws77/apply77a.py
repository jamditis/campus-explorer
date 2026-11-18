# ws77a: planted median island under T_LondonPlane_0245 / T_SugarMaple_0244 / T_RedMaple_0239 (2020 ortho shows a long grass/mulch island between the accessible row and the Sprague N row; ws76 lot mask filled it in as asphalt)
import bpy,bmesh,math
from mathutils import Vector
POLY=eval(open('/workspace/nj-scenes/montclair-state/scripts/ws77/island_poly.txt').read())
NAME='WS77_lot_median_island_ortho2020_UNVERIFIED_edges'
old=bpy.data.objects.get(NAME)
if old: bpy.data.objects.remove(old)
lots=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('WS76_accessible_lot') or o.name.startswith('WS75_sprague_lot') or o.name.startswith('WS68_RHD_ground'))]
print('WS77 lots',[o.name for o in lots],flush=True)
from mathutils.bvhtree import BVHTree
def _bvh(o):
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]
    return BVHTree.FromPolygons(V,[tuple(f.vertices) for f in o.data.polygons])
TREES={o.name:_bvh(o) for o in lots}
def zat(x,y):
    best=None
    for o in lots:
        loc,nn,i,d=TREES[o.name].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if loc and (best is None or loc.z>best): best=loc.z
    return best
# densify outline every ~1 m
pts=[]
for i in range(len(POLY)):
    a=Vector(POLY[i]); b=Vector(POLY[(i+1)%len(POLY)]); n=max(1,int((b-a).length/1.0))
    for j in range(n): pts.append(a.lerp(b,j/n))
prim=[o for o in lots if not o.name.startswith('WS68')]
def zat2(x,y):
    global lots
    sv=lots; lots=prim; z=zat(x,y); lots=sv
    return z if z is not None else zat(x,y)
raw=[zat2(p.x,p.y) for p in pts]
import numpy as np
A=np.array([[p.x,p.y,1] for p,z in zip(pts,raw) if z is not None]); Z=np.array([z for z in raw if z is not None])
cf=np.linalg.lstsq(A,Z,rcond=None)[0]; res=Z-A@cf
print('WS77 plane',cf,'resid max',abs(res).max(),'p90',np.percentile(abs(res),90),flush=True)
# per-vertex: plane, but lift to cover any lot hit above plane (clip outliers >0.4 m)
# follow the lot per vertex (it has a ~1.3 m cross-fall at the W tip); misses -> nearest hit along the outline, else plane
zs=[]
n=len(pts)
for i,(p,z) in enumerate(zip(pts,raw)):
    if z is None:
        for k in range(1,n):
            for j in (i-k,i+k):
                if raw[j%n] is not None: z=raw[j%n]; break
            if z is not None: break
    zs.append(z if z is not None else cf[0]*p.x+cf[1]*p.y+cf[2])
good=Z
print('WS77 lot z range',min(good),max(good),'miss',len(pts)-len(good),flush=True)
CURB=0.15
bm=bmesh.new()
top=[bm.verts.new((p.x,p.y,z+CURB)) for p,z in zip(pts,zs)]
bot=[bm.verts.new((p.x,p.y,z-0.06)) for p,z in zip(pts,zs)]
f=bm.faces.new(top); f.material_index=1
for i in range(len(pts)):
    j=(i+1)%len(pts); s=bm.faces.new((bot[i],bot[j],top[j],top[i])); s.material_index=0
bm.normal_update()
if f.normal.z<0: bmesh.ops.reverse_faces(bm,faces=[f])
r=bmesh.ops.inset_region(bm,faces=[f],thickness=0.15,depth=0)
for ff in r['faces']: ff.material_index=0
f.material_index=1
inner=bmesh.ops.triangulate(bm,faces=[f])['faces']
for it in range(8):
    E=list({e for ff in inner if ff.is_valid for e in ff.edges if e.calc_length()>1.2})
    if not E: break
    bmesh.ops.subdivide_edges(bm,edges=E,cuts=1,use_grid_fill=False)
    inner=[ff for ff in bm.faces if ff.material_index==1]
    bmesh.ops.triangulate(bm,faces=inner); inner=[ff for ff in bm.faces if ff.material_index==1]
iv={v for ff in inner for v in ff.verts}
bnd={v for v in iv if any(l.face.material_index==0 for l in v.link_loops)}
for v in iv:
    z=zat(v.co.x,v.co.y)
    if v in bnd: v.co.z-=0.04
    elif z is not None: v.co.z=z+CURB-0.04
print('WS77 inner faces',len(inner),'verts',len(iv),flush=True)
bm.normal_update()
for ff in bm.faces:
    if ff.normal.z<-0.1 and ff.material_index==0 and abs(ff.normal.z)>0.9: ff.normal_flip()
uv=bm.loops.layers.uv.new('UVMap')
for ff in bm.faces:
    for l in ff.loops:
        co=l.vert.co; l[uv].uv=(co.x/4.0,co.y/4.0) if ff.normal.z>0.5 else ((co.x+co.y)/2.0,co.z/0.5)
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
for ff in me.polygons: ff.use_smooth=False
mc=bpy.data.materials.get('Kasser_apron_concrete_cm'); ml=bpy.data.materials.get('WS70_berm_lawn_ortho_matched') or bpy.data.materials.get('Lawn_Varied_Oct_local_fade')
me.materials.append(mc); me.materials.append(ml)
ob=bpy.data.objects.new(NAME,me)
tgt=lots[0].users_collection[0] if lots else bpy.context.scene.collection
tgt.objects.link(ob)
print('WS77 island built verts',len(me.vertices),'mats',mc and mc.name,ml and ml.name,'col',tgt.name,flush=True)
for tn in ('T_LondonPlane_L1_0245','T_SugarMaple_L1_0244','T_RedMaple_L1_0239'):
    t=bpy.data.objects.get(tn)
    if t:
        bb=[t.matrix_world@Vector(c) for c in t.bound_box]; print('WS77 tree',tn,'base z',round(min(p.z for p in bb),2),'loc',tuple(round(v,2) for v in t.matrix_world.translation),'lotz',zat(t.matrix_world.translation.x,t.matrix_world.translation.y),flush=True)

# ws83a: smooth flush concrete edge band (curb strip) along the WEST edge of the Footpaths_OSM walk beside the WS82 Sprague lane.
# Hides the walk's sawtooth edge and the dark slits/green slivers at the lane/walk seam. Width/height UNVERIFIED (no source for a curb).
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    b=bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); return t
FP=bpy.data.objects['Footpaths_OSM']; LN=bpy.data.objects['WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges']
FB=bvh(FP); LB=bvh(LN)
def hz(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; return h.z if h else None
b=bmesh.new(); b.from_mesh(FP.data); b.transform(FP.matrix_world)
Y0,Y1=-131.0,-106.5
fs=set(f for f in b.faces if -225<f.calc_center_median().x<-212 and Y0-1<f.calc_center_median().y<Y1+1)
pts=[]
for f in fs:
    c=f.calc_center_median()
    for e in f.edges:
        if sum(1 for g in e.link_faces if g in fs)!=1: continue
        a,d=e.verts[0].co,e.verts[1].co; m=(a+d)/2; t=(d-a); t.z=0
        if t.length<1e-4: continue
        n=Vector((-t.y,t.x,0)).normalized()
        if n.dot(Vector((m.x-c.x,m.y-c.y,0)))<0: n=-n
        if n.x>-0.5: continue
        if hz(LB,m.x-0.4,m.y) is None: continue
        if hz(FB,m.x-0.15,m.y) is not None: continue
        pts+= [(a.x,a.y,a.z),(d.x,d.y,d.z)]
print('WS83a west-edge pts',len(pts),flush=True)
if len(pts)<6: raise SystemExit('WS83a ABORT too few edge pts')
STEP=0.5; ys=[Y0+k*STEP for k in range(int((Y1-Y0)/STEP)+1)]
raw=[]
for y in ys:
    q=[p for p in pts if abs(p[1]-y)<=0.6]
    raw.append((min(p[0] for p in q),max(p[2] for p in q)) if q else None)
# fill gaps by interpolation, then smooth x (5-tap)
idx=[i for i,r in enumerate(raw) if r]
print('WS83a bins',len(ys),'filled',len(idx),'x range',min(raw[i][0] for i in idx),max(raw[i][0] for i in idx),flush=True)
for i in range(len(raw)):
    if raw[i] is None:
        lo=max([j for j in idx if j<i],default=None); hi=min([j for j in idx if j>i],default=None)
        if lo is None: raw[i]=raw[hi]
        elif hi is None: raw[i]=raw[lo]
        else:
            w=(i-lo)/(hi-lo); raw[i]=(raw[lo][0]*(1-w)+raw[hi][0]*w, raw[lo][1]*(1-w)+raw[hi][1]*w)
xs=[r[0] for r in raw]
sx=[sum(xs[max(0,i-2):i+3])/len(xs[max(0,i-2):i+3]) for i in range(len(xs))]
W_OUT,W_IN=0.10,0.22  # band: 0.10 m west of the smoothed walk edge to 0.22 m east (over the ragged edge)
bm=bmesh.new(); rows=[]
for i,y in enumerate(ys):
    xo=sx[i]-W_OUT; xi=sx[i]+W_IN
    zw=hz(FB,xi,y)
    if zw is None: zw=raw[i][1]
    zt=max(zw,raw[i][1])+0.010
    zl=hz(LB,xo-0.05,y)
    zb=(zl if zl is not None else zt-0.15)-0.03
    rows.append([bm.verts.new((xo,y,zb)),bm.verts.new((xo,y,zt)),bm.verts.new((xi,y,zt)),bm.verts.new((xi,y,zt-0.04))])
for i in range(len(rows)-1):
    a,c=rows[i],rows[i+1]
    for k in range(3): bm.faces.new((a[k],c[k],c[k+1],a[k+1]))
bm.faces.new(tuple(reversed(rows[0]))); bm.faces.new(tuple(rows[-1]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.y*0.5,(l.vert.co.x+l.vert.co.z)*0.5)
NAME='WS83_sprague_lane_walk_edge_band_concrete_UNVERIFIED'
old=bpy.data.objects.get(NAME)
if old: bpy.data.objects.remove(old)
ST=(min(r[1].co.z for r in rows),max(r[1].co.z for r in rows),max(r[1].co.z-r[0].co.z for r in rows))
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new(NAME,me)
cands=[m for m in bpy.data.materials if 'curb' in m.name.lower() and 'ws73' in m.name.lower()] or [m for m in bpy.data.materials if 'curb' in m.name.lower() and 'concrete' in m.name.lower()] or [FP.data.materials[0]]
me.materials.append(cands[0])
for c in LN.users_collection: c.objects.link(ob)
print('WS83a band rows',len(rows),'mat',cands[0].name,'zt/zt/reveal',ST,flush=True)
bpy.ops.wm.save_mainfile(); print('WS83a SAVED',flush=True)

# ws73c: (a) Kasser frontage slabs WS72 / WS71 (+ mulch bed) / WS72b sat 9-20 cm BELOW the College Ave north curb top (ws71/72 took the
# curb level from the curb's old sloped back-bottom), exposing the curb back as a stepped pale band. Raise each slab row so its curb-side edge
# = curb top + 1 cm (uniform per row, keeps the 1.5% cross-fall); WS72 west 4 m ramp to the SE crosswalk landing tapered (no change at x<=-255.5).
# (b) lawn bend x -206..-195 (no slab): WS73_curb_back_lawn_verge_UNVERIFIED strip from curb top -3 cm down to the terrain over 0.9 m.
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
c=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; V=c.data.vertices
R=[[V[6*r+k].co.copy() for k in range(6)] for r in range(len(V)//6)]
R=[v for v in R if -262<v[0].x<-190 and v[0].y>-95]; R.sort(key=lambda v:v[4].x)
def top(x):
    for a,b in zip(R,R[1:]):
        if a[4].x<=x<=b[4].x:
            t=(x-a[4].x)/((b[4].x-a[4].x) or 1); return max(a[2].z,a[3].z)*(1-t)+max(b[2].z,b[3].z)*t
    return None
from collections import defaultdict
def raise_obj(n,taper=None,ref=None):
    o=bpy.data.objects.get(n)
    if not o or o.get('ws73_raised'): print('W73c skip',n); return
    me=o.data; g=defaultdict(list)
    for v in me.vertices: g[round(v.co.x,1)].append(v)
    ds=[]
    for x,vs in g.items():
        t=top(x)
        if t is None: continue
        src=ref.get(x) if ref else None
        if src is None:
            y0=min(v.co.y for v in vs); src=max(v.co.z for v in vs if abs(v.co.y-y0)<0.02)
        d=t+0.01-src
        if taper: d*=max(0,min(1,(x-taper[0])/(taper[1]-taper[0])))
        if 0<d<0.35:
            for v in vs: v.co.z+=d
            ds.append(d)
        if ref is None: DREF[n][x]=d if 0<d<0.35 else 0
    me.update(); o['ws73_raised']=1
    print('W73c raised',n[:40],'rows',len(ds),'d min/max',round(min(ds),3) if ds else None,round(max(ds),3) if ds else None,flush=True)
DREF=defaultdict(dict)
raise_obj('WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width',taper=(-255.5,-250.5))
raise_obj('WS71_Kasser_S_sidewalk_ortho2020_UNVERIFIED_width')
raise_obj('WS72b_Kasser_S_sidewalk_east_to_Cole_UNVERIFIED_width')
# mulch bed: raise by the same per-x delta as the ws71 walk
o=bpy.data.objects['WS71_Kasser_S_wallfoot_mulch_bed_UNVERIFIED']
if not o.get('ws73_raised'):
    ref=DREF['WS71_Kasser_S_sidewalk_ortho2020_UNVERIFIED_width']; ks=sorted(ref)
    for v in o.data.vertices:
        k=min(ks,key=lambda q:abs(q-v.co.x)) if ks else None
        if k is not None: v.co.z+=ref[k]
    o.data.update(); o['ws73_raised']=1; print('W73c bed raised')
# helpers of the ws71/72/72b terrain cuts follow their slabs (raise same delta) -> they only push terrain down; leaving them is safe, skip.
# (b) lawn verge strip
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    ob=bpy.data.objects[n]; oe=ob.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(ob.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
T=bvh('Terrain_LiDAR_DTM_1m'); dn=lambda x,y:T.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
name='WS73_curb_back_lawn_verge_UNVERIFIED'
old=bpy.data.objects.get(name)
if old: bpy.data.objects.remove(old)
me=bpy.data.meshes.new(name); bm=bmesh.new(); prev=None; nr=0; under=0
for v in R:
    if not (-206.2<v[4].x<-194.5): prev=None; continue
    d=(v[4]-v[1]); d.z=0; d.normalize(); tz=max(v[2].z,v[3].z); row=[]
    for s in (0.0,0.15,0.35,0.6,0.9):
        p=v[4]+d*s; h=dn(p.x,p.y); gz=h.z if h else tz-0.2
        w=s/0.9; z=(tz-0.03)*(1-w)+(gz+0.01)*w if s>0 else tz-0.03
        if s==0.0: p=v[4]-d*0.02
        if h and h.z>z: under+=1
        row.append(bm.verts.new((p.x,p.y,z)))
    if prev:
        for k in range(len(row)-1): bm.faces.new((prev[k],prev[k+1],row[k+1],row[k]))
    prev=row; nr+=1
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
uv=me.uv_layers.new(name='UVMap')
for l in me.loops: cc=me.vertices[l.vertex_index].co; uv.data[l.index].uv=(cc.x/2,cc.y/2)
ob=bpy.data.objects.new(name,me); bpy.context.scene.collection.objects.link(ob)
mat=bpy.data.materials.get('WS70_berm_lawn_ortho_matched'); me.materials.append(mat)
print('W73c verge rows',nr,'terrain above verge pts',under,'mat',mat and mat.name,flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W73c SAVED',flush=True)

# ws136a: UNIFY #44 -- Skyline Way W walk N of -248.5 (OSM footway 312845863, replaces rippled UA_footway drape) + BK lot E-edge & W-end curbs.
import bpy, bmesh, os, math, json, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/ws134/'
exec(open(D+'dtm_helpers.py').read())
OSM=json.load(open(D+'osm134.json')); BK=[(a,b) for a,b in OSM['312845862'][:-1]]
col=bpy.data.collections.get('WS136_Skyline_W_walk_and_lot_curbs') or bpy.data.collections.new('WS136_Skyline_W_walk_and_lot_curbs')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS136a_')]: bpy.data.objects.remove(o)
cm=bpy.data.materials['WS27_curb_concrete_UNVERIFIED']; wm=bpy.data.materials.get('WS3_Concrete_panels_sawcut')
def lz(x,y): return dtm(x,y)
def smooth(a,w):
    a=np.asarray(a,float); k=np.ones(w)/w; p=np.pad(a,(w//2,w//2),mode='edge'); return np.convolve(p,k,mode='valid')
# ---- walk centreline (OSM 312845863, joins ws135 walk start at (-71.9,-248.5))
WC=[(-71.9,-248.5),(-71.8,-236.4),(-71.7,-212.5),(-71.3,-206.4),(-71.0,-203.0)]
pts=[]
for k in range(len(WC)-1):
    a=np.array(WC[k]); b=np.array(WC[k+1]); L=np.linalg.norm(b-a)
    for s in np.arange(0,L,0.5): pts.append(a+(b-a)*s/L)
pts.append(np.array(WC[-1])); pts=np.array(pts)
px=smooth(pts[:,0],13); px[0]=pts[0,0]; px[-1]=pts[-1,0]; py=pts[:,1]
zc=np.array([lz(x,y) for x,y in zip(px,py)]); zs=smooth(zc,15)
zs[:3]=zc[:3]  # join ws135 walk end (uses dtm+0.07 there)
HW=1.15; bm=bmesh.new(); rows=[]
for k in range(len(px)):
    d=np.array([px[min(k+1,len(px)-1)]-px[max(k-1,0)],py[min(k+1,len(px)-1)]-py[max(k-1,0)]]); d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])
    r=[]
    for t in np.linspace(-HW,HW,5):
        u=np.array([px[k],py[k]])+n*t
        # 1.5 % cross-fall to the road (E = +x side)
        east=(1 if n[0]>0 else -1)*t
        r.append(bm.verts.new((u[0],u[1],zs[k]+0.07-0.015*(east+HW))))
    rows.append(r)
for i in range(len(rows)-1):
    for j in range(4): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for j in (0,4):
    sk=[bm.verts.new((r[j].co.x,r[j].co.y,r[j].co.z-0.4)) for r in rows]
    for i in range(len(rows)-1): bm.faces.new((rows[i][j],rows[i+1][j],sk[i+1],sk[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('WS136a_Skyline_W_walk_N_of_-248_OSM312845863_graded_2p3m_UNVERIFIEDjoints'); bm.to_mesh(me); bm.free()
if wm: me.materials.append(wm)
uvl=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uvl.data[lp.index].uv=(p.x/2.0,p.y/2.0)
bm=bmesh.new(); bm.from_mesh(me)
for f in bm.faces:
    if abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
col.objects.link(bpy.data.objects.new(me.name,me))
# ---- curbs for BK lot E edge and W end (same section as ws135 S curb); skip parts inside/against BK
def curbmesh(name,LS,sgn):
    bm=bmesh.new(); pts=[]
    for k in range(len(LS)-1):
        a=np.array(LS[k]); b=np.array(LS[k+1]); L=np.linalg.norm(b-a)
        for s in np.arange(0,L,1.0): pts.append(a+(b-a)*s/L)
    pts.append(np.array(LS[-1])); rings=[]
    for k,p in enumerate(pts):
        q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([d[1],-d[0]])*sgn
        z=lz(p[0],p[1])+0.05; a=p; b=p-n*0.18
        rings.append([bm.verts.new((a[0],a[1],z-0.2)),bm.verts.new((a[0],a[1],z+0.12)),bm.verts.new((b[0],b[1],z+0.12)),bm.verts.new((b[0],b[1],z-0.2))])
    for i in range(len(rings)-1):
        for j in range(3): bm.faces.new((rings[i][j],rings[i+1][j],rings[i+1][j+1],rings[i][j+1]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    m=bpy.data.meshes.new(name); bm.to_mesh(m); bm.free(); m.materials.append(cm); col.objects.link(bpy.data.objects.new(name,m))
# E edge: x=-91 from y -269.4 down to -280.9 (outward +x); curb on the edge line, outside offset handled by sign
curbmesh('WS136a_BK_lot_E_edge_curb_ortho2020_UNVERIFIEDreveal',[(-91.0,-269.4),(-91.0,-280.9)],1)
# W end: x=-121.5 from y -277.3 up to -263 (outward -x), but stop 0.6 m short of BK wall
ytop=-263.0
while pip(BK,-121.5,ytop-0.6) or pip(BK,-121.6,ytop-0.6): ytop-=0.5
curbmesh('WS136a_BK_lot_W_end_curb_ortho2020_UNVERIFIEDreveal',[(-121.5,-277.3),(-121.5,ytop-0.6)],-1)
# ---- retire old rippled faces under the new walk
def retire(oname,box):
    o=bpy.data.objects.get(oname)
    if not o: return 0
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    dl=[f for f in bm.faces if (lambda c:box[0]<=c.x<=box[1] and box[2]<=c.y<=box[3])(mw@f.calc_center_median())]
    if dl: bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(o.data)
    bm.free(); return len(dl)
for nm in ('UA_footway_312845863_south_UNVERIFIED','Footpaths_OSM'):
    print('RETIRED',nm,retire(nm,(-74.6,-68.8,-249.0,-203.0)))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')

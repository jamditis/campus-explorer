# ws269 (merge208 CHAIN, on main ws268c): UNIFY W72b — College Ave / Lot 33 paint + planted tree island + island tree.
# Evidence: NJ 2020 Natural ortho via img.nj.gov WMS (url269.txt, 0.1 m/px). paint269.py: bright thin top-hat strokes inside the ws268
# polygon -> PCA line segments (paint269k.json, 31 kept: N-side parallel-stall ticks, centre-line dashes, crosswalk bar pieces, angled
# stall lines along the Maintenance Building, gore lines at the Carlisle Rd end); car glare, tree, and turn-arrow blobs dropped by box.
# Island: the dark mulch band (-357.5,-36.6)->(-334.5,-40.9), ~2.6 m wide, rounded ends; 15 cm concrete curb, mulch 5 cm under the curb top.
# Tree: one linked duplicate of the WS165 red maple on the island, under the ortho crown (~11 m across -> h ~13 m), species/trunk UNVERIFIED.
# Everything sits ON the WS268 paving (raycast on its base mesh): paint +1.2 cm; no terrain or paving verts edited.
import bpy, bmesh, json, math, numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
TAG='F269A'; OB=bpy.data.objects; D=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws269/paint269k.json'))
if OB.get('WS269_W72b_CollegeAve_Lot33_paint_ortho2020_UNVERIFIED'): raise SystemExit('F269A already applied')
pav=OB['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(pav.data); bm.transform(pav.matrix_world)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.normal.z<0.5],context='FACES')   # top only (no skirts)
TP=BVHTree.FromBMesh(bm); bm.free()
def pz(x,y):
    r=TP.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return None if r[0] is None else r[0].z
def mat(*keys):
    for k in keys:
        for m in bpy.data.materials:
            if k in m.name: return m
    return None
col=pav.users_collection[0]
# --- paint strips
mp=mat('WS76_lot_stall_paint_white','stall_paint_white','es_rhd_stall_paint_worn')
bm=bmesh.new(); npt=0; nsk=0
for x0,y0,x1,y1,w in D['segs']:
    L=math.hypot(x1-x0,y1-y0); d=Vector(((x1-x0)/L,(y1-y0)/L)); n=Vector((-d.y,d.x))*(w/2); k=max(1,int(L/0.5)); row=[]
    ok=True
    for i in range(k+1):
        p=Vector((x0,y0))+d*(L*i/k); za=pz(*(p+n)); zb=pz(*(p-n))
        if za is None or zb is None: ok=False; break
        row.append((bm.verts.new(((p+n).x,(p+n).y,za+0.012)),bm.verts.new(((p-n).x,(p-n).y,zb+0.012))))
    if not ok:
        for r in row:
            for v in r: bm.verts.remove(v)
        nsk+=1; continue
    for (a,b),(c,e) in zip(row[:-1],row[1:]): bm.faces.new((a,b,e,c))
    npt+=1
me=bpy.data.meshes.new('WS269_W72b_paint'); bm.to_mesh(me); bm.free()
if mp: me.materials.append(mp)
o=OB.new('WS269_W72b_CollegeAve_Lot33_paint_ortho2020_UNVERIFIED',me); col.objects.link(o)
o['ws269']='paint strokes traced from NJ 2020 ortho (0.1 m WMS); widths 10-20 cm; turn arrows and hatches not modelled'
print(TAG,'paint segs',npt,'skipped(off paving)',nsk,'mat',mp and mp.name,'faces',len(me.polygons),flush=True)
# --- island (stadium outline)
I=D['island']; A=Vector(I['a']); B=Vector(I['b']); R=I['w']/2; dv=(B-A).normalized(); nv=Vector((-dv.y,dv.x))
def outline(r,step=0.35):
    pts=[]; L=(B-A).length; m=max(2,int(L/step))
    for i in range(m+1): pts.append(A+dv*(L*i/m)+nv*r)
    for i in range(1,12): t=math.pi/2-math.pi*i/12; pts.append(B+dv*(r*math.cos(t))+nv*(r*math.sin(t)))
    for i in range(m+1): pts.append(B+dv*(-L*i/m)-nv*r)
    for i in range(1,12): t=-math.pi/2-math.pi*i/12; pts.append(A+dv*(r*math.cos(t))+nv*(r*math.sin(t)))
    return pts
OUT=outline(R); INN=outline(R-0.15)
zs=[pz(p.x,p.y) for p in OUT]; zbase=[z for z in zs if z is not None]
print(TAG,'island paving z min/max',round(min(zbase),3),round(max(zbase),3),'missing',zs.count(None),flush=True)
def zt(p): z=pz(p.x,p.y); return (z if z is not None else min(zbase))+0.15
bm=bmesh.new()
vo=[bm.verts.new((p.x,p.y,zt(p))) for p in OUT]; vb=[bm.verts.new((p.x,p.y,zt(p)-0.25)) for p in OUT]
vi=[bm.verts.new((p.x,p.y,zt(p))) for p in INN]; vib=[bm.verts.new((p.x,p.y,zt(p)-0.05)) for p in INN]
N=len(OUT)
for i in range(N):
    j=(i+1)%N
    bm.faces.new((vb[i],vb[j],vo[j],vo[i]))      # outer curb face
    bm.faces.new((vo[i],vo[j],vi[j],vi[i]))      # curb top
    bm.faces.new((vi[i],vi[j],vib[j],vib[i]))    # inner reveal
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]); bm.normal_update()
tops=[f for f in bm.faces if abs(f.normal.z)>0.5]
if sum(f.normal.z for f in tops)<0:
    for f in bm.faces: f.normal_flip()
mc=mat('Paving_concrete','KX_drive_concrete','ge_walk_concrete')
me=bpy.data.meshes.new('WS269_W72b_island_curb'); bm.to_mesh(me); bm.free()
if mc: me.materials.append(mc)
oc=OB.new('WS269_W72b_Lot33_tree_island_curb_ortho2020_UNVERIFIED',me); col.objects.link(oc)
# mulch top (fan from the centreline points)
bm=bmesh.new(); ring=[bm.verts.new((p.x,p.y,zt(p)-0.05)) for p in INN]; f=bm.faces.new(ring)
bmesh.ops.triangulate(bm,faces=[f]);
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
mm=mat('mulch','ge_bed_soil')
me=bpy.data.meshes.new('WS269_W72b_island_mulch'); bm.to_mesh(me); bm.free()
if mm: me.materials.append(mm)
om=OB.new('WS269_W72b_Lot33_tree_island_mulch_UNVERIFIED',me); col.objects.link(om)
print(TAG,'island curb faces',len(oc.data.polygons),'mat',mc and mc.name,'mulch mat',mm and mm.name,flush=True)
# --- tree
src=[o for o in OB if o.name.startswith('WS165_tree_aisle_mouth')][0]
_mw=src.matrix_world; _W=[_mw@v.co for v in src.data.vertices]; _zm=min(w.z for w in _W); _L=[w for w in _W if w.z<_zm+0.3]
B0=Vector((sum(w.x for w in _L)/len(_L),sum(w.y for w in _L)/len(_L),_zm))
tx,ty,h=-347.5,-38.4,13.0; s=h/18.0; b=Vector((tx,ty,pz(tx,ty)+0.10-0.12))
M=Matrix.Translation(b)@Matrix.Rotation(2.1,4,'Z')@Matrix.Diagonal((s,s,s,1))@Matrix.Translation(-B0)@src.matrix_world
t=OB.new('WS269_tree_Lot33_island_ortho2020_h13m_UNVERIFIEDspecies',src.data); src.users_collection[0].objects.link(t); t.matrix_world=M
for i,sl in enumerate(src.material_slots):
    if sl.link=='OBJECT': t.material_slots[i].link='OBJECT'; t.material_slots[i].material=sl.material
print(TAG,'tree',t.name,'base z',round(b.z,2),flush=True)

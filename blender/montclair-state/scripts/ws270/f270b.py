# ws270b (merge208 CHAIN, on ws270a): College Ave / Lot 33 paving edge skirt -> graded ground shoulder where the ground falls away.
# The f268c skirt hangs 0.6 m straight down; where the paving edge stands 0.1-0.5 m above the ground outside (S/SW edge by
# Carlisle Rd) the vertical asphalt strip showed from above as a dark sawtooth cut by the terrain triangles. Each skirt vertex whose
# outward ground is lower than its top partner is moved outward (2x the drop, 0.25-1.2 m) and down to that ground - 5 cm, and the
# skirt faces get a lawn material, so the edge reads as a grass shoulder. Where the ground outside is higher (N curb, lawn foot) or
# the outward point is still inside the polygon (holes under the walk/deck), the skirt stays vertical and buried. No terrain edits.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F270B'; OB=bpy.data.objects; NAME='WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED'
P=[(-336,-25.2),(-345,-23.0),(-355,-21.5),(-367,-20.6),(-378,-20.0),(-390,-19.5),(-390,-36),(-387,-39),(-376,-42),(-377,-46),
   (-327,-59),(-317,-61),(-315,-61),(-311,-48),(-318,-31),(-331,-27.2)]
def pip(x,y):
    c=False; n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]
        if (y0>y)!=(y1>y) and x<x0+(y-y0)*(x1-x0)/(y1-y0): c=not c
    return c
def outn(x,y):
    best=(1e9,None); n=len(P)
    for i in range(n):
        (x0,y0),(x1,y1)=P[i],P[(i+1)%n]; dx,dy=x1-x0,y1-y0; t=max(0,min(1,((x-x0)*dx+(y-y0)*dy)/(dx*dx+dy*dy)))
        d=((x-x0-t*dx)**2+(y-y0-t*dy)**2)**.5
        if d<best[0]: L=(dx*dx+dy*dy)**.5; best=(d,Vector((dy/L,-dx/L)))
    nv=best[1]
    if pip(x+nv.x*0.3,y+nv.y*0.3): nv=-nv
    return best[0],nv
GN=('WS68_RHD_ground_northDTM','M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam')
gobs=[o for o in OB if o.type=='MESH' and o.name.startswith(GN)]
for o in gobs:
    for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); GT=[]
for o in gobs:
    oe=o.evaluated_get(dg); me=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not any(-396<v.co.x<-305 and -67<v.co.y<-14 for v in f.verts)],context='FACES')
    GT.append(BVHTree.FromBMesh(bm)); bm.free(); oe.to_mesh_clear()
for o in gobs:
    for m in o.modifiers: m.show_viewport=False
def gz(x,y):
    b=None
    for t in GT:
        r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if r[0] is not None and (b is None or r[0].z>b): b=r[0].z
    return b
pav=OB[NAME]; me=pav.data; mw=pav.matrix_world; mi=mw.inverted()
print(TAG,'paving identity',mw==__import__('mathutils').Matrix.Identity(4),'M3b identity',[o.matrix_world==__import__('mathutils').Matrix.Identity(4) for o in gobs],flush=True)
bm=bmesh.new(); bm.from_mesh(me)
top=set(v for f in bm.faces if f.normal.z>0.3 for v in f.verts)
key={}
for v in top: w=mw@v.co; key[(round(w.x,3),round(w.y,3))]=w.z
moved=kept=0; drops=[]; MV=set()
for v in bm.verts:
    if v in top: continue
    w=mw@v.co; zt=key.get((round(w.x,3),round(w.y,3)))
    if zt is None: kept+=1; continue
    d,nv=outn(w.x,w.y)
    if d>0.05: kept+=1; continue          # an inner hole edge (walk/deck), not the outline
    drop=None
    for s in (0.25,0.5,0.8,1.2):
        g=gz(w.x+nv.x*s,w.y+nv.y*s)
        if g is None: break
        if zt-g<0.02: break
        drop=(s,g)
        if zt-g<=2*s: break
    if drop is None: kept+=1; continue
    s=min(1.2,max(0.25,2*(zt-drop[1]))); g=gz(w.x+nv.x*s,w.y+nv.y*s)
    if g is None or zt-g<0.02: kept+=1; continue
    w2=Vector((w.x+nv.x*s,w.y+nv.y*s,g-0.05)); v.co=mi@w2; moved+=1; MV.add(v); drops.append(zt-g)
lawn=bpy.data.materials.get('North_ground_ortho2020.001')   # the adjacent M3b ground's own ortho material (Object coords; both objects have identity transforms)
if lawn and lawn.name not in [m.name for m in me.materials if m]: me.materials.append(lawn)
li=[m.name if m else None for m in me.materials].index(lawn.name) if lawn else 0
ns=0
for f in bm.faces:
    if any(v in MV for v in f.verts): f.material_index=li; ns+=1   # graded shoulder faces only (buried/hole skirts keep asphalt)
bm.to_mesh(me); bm.free(); me.update()
print(TAG,'skirt verts moved',moved,'kept vertical',kept,'drop p50/max',np.round([np.median(drops),max(drops)],2) if drops else None,'skirt faces lawn',ns,'material',lawn and lawn.name,flush=True)
pav['ws270b']='edge skirt graded into a lawn shoulder where the ground falls away'

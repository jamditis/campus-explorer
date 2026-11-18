# ws196 WOBBLE W14: WS76 accessible-stall markings (Red Hawk/Kasser accessible lot, 2 rows x 9 stalls).
# Found (probe196b): the "symbol stand-ins" were 4 overlapping objects (base fan + .003 = 18 flat 16-gon discs, .001/.002 = exact
# duplicates of 5 of them). The discs were PLANAR on a sloped/faceted lot: one side floated up to 7 cm over the asphalt, the other
# dipped 1 cm under -> grey raised slabs with jagged z-fight edges; the duplicates sat exactly ON the asphalt (z 0) -> z-fight.
# Fix: delete all four; build ONE flat painted International Symbol of Accessibility (white, standard US stall marking; exact
# glyph/size/orientation UNVERIFIED — the 2020 ortho only resolves the blue squares) per stall at the old disc centres, as a finely
# tessellated (<=0.08 m) decal draped vertex-by-vertex 2.2 cm over the top-most asphalt (blue paint re-draped at 1.5 cm, so paint
# is a clean thin layer, no float, no dip). Blue paint (lines + 1.5 m squares) densified (edges <=0.35 m) and re-draped too.
import bpy,bmesh,math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
lots=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch'))]
print('F196 lots',[o.name for o in lots],flush=True)
TR=[]
for o in lots:
    mw=o.matrix_world; TR.append(BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]))
def zat(x,y):
    b=None
    for T in TR:
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] and (b is None or h[0].z>b): b=h[0].z
    return b
# --- old symbol objects: centres + material, then delete
names=[n for n in bpy.data.objects.keys() if n.startswith('WS76_lot_accessible_symbol_standin_UNVERIFIED')]
src=bpy.data.objects['WS76_lot_accessible_symbol_standin_UNVERIFIED.003']; m=src.matrix_world
C=[]
for f in src.data.polygons:
    c=sum((m@src.data.vertices[k].co for k in f.vertices),Vector())/len(f.vertices); C.append((c.x,c.y))
mat=src.data.materials[0]; col=src.users_collection[0]
for n in names: bpy.data.objects.remove(bpy.data.objects[n])
print('F196 removed',names,'centres',len(C),flush=True)
C=np.array(C)
# row direction from each row's centres (two rows of 9)
rows=[C[:9],C[9:]]
# --- glyph pieces in local (u=across stall/right, v=up the stall) metres, ISA ~0.95 m tall
def bar(p,q,w,st=0.07):
    p=np.array(p);q=np.array(q);d=q-p;L=np.linalg.norm(d);t=d/L;n=np.array((-t[1],t[0]))*w/2;k=max(1,int(math.ceil(L/st)))
    V=[];F=[]
    for i in range(k+1):
        a=p+d*i/k; V+= [a-n,a+n]
    for i in range(k): F.append((2*i,2*i+2,2*i+3,2*i+1))
    return V,F
def ring(c,ro,ri,a0,a1,n=40):
    V=[];F=[]
    for i in range(n+1):
        a=math.radians(a0+(a1-a0)*i/n); e=np.array((math.cos(a),math.sin(a))); V+=[np.array(c)+e*ri,np.array(c)+e*ro]
    for i in range(n): F.append((2*i,2*i+2,2*i+3,2*i+1))
    return V,F
def disc(c,r,n=20):
    V=[np.array(c)]+[np.array(c)+r*np.array((math.cos(2*math.pi*i/n),math.sin(2*math.pi*i/n))) for i in range(n)]
    F=[(0,1+i,1+(i+1)%n) for i in range(n)]; return V,F
G=[disc((0.02,0.40),0.075), bar((0.0,0.30),(0.0,0.02),0.075), bar((0.0,0.19),(0.20,0.19),0.06),
   bar((-0.035,0.02),(0.24,0.02),0.075), bar((0.24,0.02),(0.33,-0.22),0.07), ring((-0.03,-0.12),0.29,0.22,75,375)]
bm=bmesh.new(); miss=0; nv=0
for R in rows:
    t=R[-1]-R[0]; t=t/np.linalg.norm(t); up=np.array((-t[1],t[0]))  # stall axis (perpendicular to row)
    for c in R:
        for gi,(V,F) in enumerate(G):
            vs=[]
            for p in V:
                x,y=c+t*p[0]+up*p[1]; z=zat(x,y)
                if z is None: miss+=1; z=zat(c[0],c[1]) or 0
                vs.append(bm.verts.new((x,y,z+0.022+0.0005*gi)))
            for f in F: bm.faces.new([vs[i] for i in f])
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
NAME='WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED'
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free(); me.materials.append(mat)
ob=bpy.data.objects.new(NAME,me); col.objects.link(ob)
print('F196 ISA verts',len(me.vertices),'faces',len(me.polygons),'miss',miss,flush=True)
# --- all WS76 paint decals (blue accessible, white stall lines, zebra): densify + re-drape at +1.5 cm (white lines/zebra were
# also planar strips floating/dipping on the faceted lot -> raised-bar look with dark lips in the NE-aisle eye view)
for PN in ('WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED','WS76_lot_stall_paint_white_ortho2020_UNVERIFIED','WS76_lot_zebra_walkway_paint_ortho2020_UNVERIFIED'):
    B=bpy.data.objects[PN]; mw=B.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(B.data)
    for it in range(6):
        E=[e for e in bm.edges if ((mw@e.verts[0].co)-(mw@e.verts[1].co)).length>0.35]
        if not E: break
        bmesh.ops.subdivide_edges(bm,edges=E,cuts=1,use_grid_fill=True)
    bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
    dz=[];bm_miss=0
    for v in bm.verts:
        w=mw@v.co; z=zat(w.x,w.y)
        if z is None: bm_miss+=1; continue
        dz.append(w.z-(z+0.015)); w.z=z+0.015; v.co=mi@w
    bm.to_mesh(B.data); B.data.update(); n=len(bm.verts); bm.free()
    dz=np.array(dz); print('F196 paint',PN[:30],'verts',n,'miss',bm_miss,'old offset vs +1.5cm: min %.3f max %.3f'%(dz.min(),dz.max()),flush=True)

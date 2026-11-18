# ws164b: (1) N lawn lip ribbon made flush with the regraded WS110 patch (its outer edge sat ~6 cm proud -> dark crease line on the bank);
# (2) curbed mulch bed at the Lot 3 aisle mouth E side (ortho 2020: dark mulch x -308..-300, y -252.5..-249 with a light concrete curb on its
#     W/N sides and a rounded NW corner; LiDAR 2023: class-2 ground flat (no shrubs), intensity ~1000 = dark mulch; it sits under the S edge
#     of a ~17 m deciduous crown centred ~(-299,-242) (LiDAR veg) — tree NOT added this pass). Bed from the walk back edge to y -248.8, x -305.45..-300.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
SL=0.236; dv=np.array([-1.0,SL]); dv/=np.linalg.norm(dv); nv=np.array([SL,1.0]); nv/=np.linalg.norm(nv); A0=np.array([-268.8,-262.9])
def npt(x): t=(A0[0]-x)/(-dv[0]); return A0+dv*t
def wb(x): return (npt(x)+nv*(0.18+3.2))[1]
def bvh(objs):
    V=[];F=[]
    for o in objs:
        b=len(V); V+=[o.matrix_world@v.co for v in o.data.vertices]; F+=[[b+i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
def hz(T,x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
pa=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']; gp=OB['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']
TG=bvh([pa,gp])
import copy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws164/fix164a.py').read().split('def ramp')[0].split('OB=bpy.data.objects',1)[1])  # dz() = smoothed LiDAR DTM

# (1) lip flush
lip=OB['WS163_walk_back_lawn_lip_N_UNVERIFIED']; mw=lip.matrix_world; mi=mw.inverted(); n=0
vs=list(lip.data.vertices)
for k in range(0,len(vs)-2,3):
    v0,v1,v2=vs[k],vs[k+1],vs[k+2]; p0=mw@v0.co; p1=mw@v1.co; p2=mw@v2.co
    g2=hz(TG,p2.x,p2.y)
    if g2 is None: continue
    p2.z=g2+0.012; g1=hz(TG,p1.x,p1.y); z1=p0.z+(p2.z-p0.z)*0.36
    if g1 is not None: z1=max(z1,g1+0.012)
    p1.z=z1; v1.co=mi@p1; v2.co=mi@p2; n+=1
lip.data.update(); print('LIP rows flushed',n)
# (2) bed
col=bpy.data.collections.get('WS163_NormalAve_W_LotS')
for o in [o for o in OB if o.name.startswith('WS164_')]: OB.remove(o)
walk=OB['WS163_NormalAve_W_N_sidewalk_3p2m_LiDAR2023_int_UNVERIFIED']; TW=bvh([walk])
def ref(x):  # walk top just inside its back edge
    z=hz(TW,x,wb(x)-0.15); return z if z is not None else hz(TG,x,wb(x))
XW,XE,YN,RC,CW=-305.45,-300.0,-248.8,1.0,0.15
# outline (outer curb face) from the walk back edge at XW, N along x=XW, arc to the N edge, E to XE
def outline(off):
    pts=[(XW-off,wb(XW)-0.05)]
    for y in np.arange(wb(XW)-0.05+0.5,YN-RC,0.5): pts.append((XW-off,y))
    cx,cy=XW+RC,YN-RC
    for a in np.linspace(math.pi,math.pi/2,7): pts.append((cx+(RC+off)*math.cos(a),cy+(RC+off)*math.sin(a)))
    for x in np.arange(cx+0.5,XE,0.5): pts.append((x,YN+off))
    pts.append((XE,YN+off)); return pts
OUT=outline(0.0); INN=outline(-CW)
def mat(n,rgb,r=0.9):
    m=bpy.data.materials.get(n)
    if m: return m
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=r; return m
cm=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED') or mat('WS27_curb_concrete_UNVERIFIED',(0.55,0.54,0.51))
mo=OB.get('WS160b_PanzerE_N_evergreen_bed_mulch_ortho2020_LiDAR'); mm=(mo.active_material if mo and mo.active_material else mat('WS164_mulch_dark_brown',(0.09,0.06,0.04),0.95))
xr=[p[0] for p in OUT]; 
def rz(x): return ref(min(max(x,XW),XE-0.2))
def mk(name,bm,m):
    for f in bm.faces:
        f.normal_update()
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    uv=me.uv_layers.new(name='UVMap')
    for lp in me.loops:
        p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.5,p.y*0.5+p.z*0.5)
    o=OB.new(name,me); (col or bpy.context.scene.collection).objects.link(o); return o
# curb: top band between OUT and INN at ref+0.15, outer vertical face down to ref-0.10
bm=bmesh.new(); To=[];Ti=[];Bo=[]
for (xo,yo),(xi,yi) in zip(OUT,INN):
    z=max(rz(xo)+0.15,dz(xo,yo)+0.08); To.append(bm.verts.new((xo,yo,z))); Ti.append(bm.verts.new((xi,yi,z))); Bo.append(bm.verts.new((xo,yo,z-0.30)))
for i in range(len(OUT)-1):
    bm.faces.new((To[i],To[i+1],Ti[i+1],Ti[i])); bm.faces.new((Bo[i],Bo[i+1],To[i+1],To[i]))
for f in bm.faces:
    f.normal_update()
    if f.calc_area()>0 and abs(f.normal.z)>0.5 and f.normal.z<0: f.normal_flip()
curb=mk('WS164_aisle_mouth_bed_curb_ortho2020_UNVERIFIEDsection',bm,cm)
# mulch: fill INN + E edge + walk back edge, top = ref+0.10, inner curb face from mulch to curb top
poly=INN+[(XE,wb(XE)-0.05)]
from mathutils.geometry import tessellate_polygon
tris=tessellate_polygon([[Vector((x,y,0)) for x,y in poly]])
bm=bmesh.new(); vv=[bm.verts.new((x,y,max(rz(x)+0.10,dz(x,y)+0.03))) for x,y in poly]
for t in tris:
    try: bm.faces.new([vv[i] for i in t])
    except ValueError: pass
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
mulch=mk('WS164_aisle_mouth_mulch_bed_ortho2020_LiDAR2023_flat',bm,mm)
print('BED curb',len(curb.data.polygons),'mulch',len(mulch.data.polygons))
# push ground under the bed
TB=bvh([curb,mulch]); pc=0
for g in (pa,gp):
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (XW-0.6<p.x<XE+0.3 and wb(XW)-1<p.y<YN+0.6): continue
        z=hz(TB,p.x,p.y)
        if z is not None and p.z>z-0.06: p.z=z-0.06; v.co=mi@p; pc+=1
    g.data.update()
print('ground pushed',pc)
t=OB.get('WS163_skirt_target_hidden')
if t:
    tb=bmesh.new(); tb.from_mesh(t.data); n0=len(tb.faces); L=tb.verts.layers.float.get('wv_in')
    for o in (curb,mulch):
        for p in o.data.polygons:
            vs_=[tb.verts.new(o.matrix_world@o.data.vertices[i].co) for i in p.vertices]
            if L:
                for v in vs_: v[L]=0.45
            try: tb.faces.new(vs_)
            except ValueError: pass
    tb.to_mesh(t.data); tb.free(); t.data.update(); print('target',n0,'->',len(t.data.polygons))

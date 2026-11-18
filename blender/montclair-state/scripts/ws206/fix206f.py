# ws206 W12 CCOM walk, part 2: the OSM walk's own E outline has V-notches (y ~-46, ~-49.5, ~-36.5) that read as bites once the
# lawn was graded flush (fix206c). Edge206 E-edge picks fit two straight runs: x = 8.45 + 0.4533*(-38 - y) (y -36..-45.6) and
# x = 11.70 - 0.157*(-47 - y) (y -45.6..-58), meeting at (11.92,-45.64) - the walk's bend. New concrete edge strip
# WS206_CCOM_walk_E_edge_straight_fill (walk material) from the fitted line 1.4 m inward, z = walk surface - 3 mm where the walk
# exists (hidden), else the nearest walk height inward (flush), so the visible E edge is the straight fitted line. Terrain under
# / within 1 m of the strip graded as in fix206c (lower-only, 0.5 m max so no deep cuts).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
FP=ob('Footpaths_OSM'); TER=ob('Terrain_LiDAR_DTM_1m')
fm=FP.matrix_world; vs=set(i for i,v in enumerate(FP.data.vertices) if -2<(fm@v.co).x<20 and -64<(fm@v.co).y<-28)
pl=[p for p in FP.data.polygons if all(i in vs for i in p.vertices)]
TF=BVHTree.FromPolygons([fm@v.co for v in FP.data.vertices],[tuple(p.vertices) for p in pl])
def xe(y): return 8.45+0.4533*(-38-y) if y>=-45.64 else 11.70-0.157*(-47-y)
h=TF.ray_cast(Vector((9.5,-45,160)),Vector((0,0,-1)),80); mat=FP.data.materials[pl[h[2]].material_index] if h[0] else FP.data.materials[0]
ys=np.r_[np.arange(-36.0,-45.64,-0.25),-45.64,np.arange(-45.75,-58.01,-0.25)]; offs=np.linspace(0,1.4,8)
bm=bmesh.new(); V={}
for i,y in enumerate(ys):
    for j,o in enumerate(offs):
        x=xe(y)-o; z=hz(TF,x,y)
        if z is not None: z-=0.003
        else:
            for dd in np.arange(0.1,1.5,0.1):
                z=hz(TF,x-dd,y)
                if z is not None: break
        V[(i,j)]=[x,y,z]
# fill any None by neighbours
for (i,j),p in V.items():
    if p[2] is None:
        zz=[V[(k,j)][2] for k in range(max(0,i-4),min(len(ys),i+5)) if V[(k,j)][2] is not None]; p[2]=float(np.mean(zz)) if zz else 0
BV={k:bm.verts.new(tuple(p)) for k,p in V.items()}
for i in range(len(ys)-1):
    for j in range(len(offs)-1): bm.faces.new([BV[(i,j)],BV[(i,j+1)],BV[(i+1,j+1)],BV[(i+1,j)]])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS206_ccom_edge'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
for p in me.polygons: p.use_smooth=True
o=bpy.data.objects.new('WS206_CCOM_walk_E_edge_straight_fill_ortho_LiDAR_UNVERIFIED',me); FP.users_collection[0].objects.link(o)
print('F206f strip faces',len(me.polygons),'mat',mat.name if mat else None,flush=True)
# terrain grade (lower-only, max 0.5 m)
mw=o.matrix_world; TS=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
def wz(x,y):
    a=hz(TF,x,y); b=hz(TS,x,y); zs=[z for z in (a,b) if z is not None]; return max(zs) if zs else None
tm=TER.matrix_world; ti=tm.inverted(); n=0; mx=0; ang=np.linspace(0,2*np.pi,17)[:-1]
for v in TER.data.vertices:
    g=tm@v.co
    if not (5<g.x<16 and -60<g.y<-33): continue
    zf=wz(g.x,g.y); cap=None
    if zf is not None: cap=zf-0.03
    else:
        for r in (0.2,0.4,0.6,0.8,1.0,1.15,1.3):
            zs=[wz(g.x+r*np.cos(a),g.y+r*np.sin(a)) for a in ang]; zs=[z for z in zs if z is not None]
            if zs: cap=min(zs)-0.01+(0.2*(r-1.0) if r>1.0 else 0); break
    if cap is not None and g.z>cap:
        cap=max(cap,g.z-0.5); mx=max(mx,g.z-cap); g.z=cap; v.co=ti@g; n+=1
TER.data.update(); print('F206f terrain graded',n,'max %.3f'%mx,flush=True)

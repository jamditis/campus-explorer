# W12c (ws240): CCOM dock apron S-edge corner E of the ws209 crossing slab. probe240a (evaluated): the apron/slab stand
# 0.3-0.6 m over a LiDAR lawn dip at x~9.5-12, y~-39.5..-42 (terrain 4.6-4.9 vs apron edge 5.4-5.6 m+130), which reads as a
# dark faceted lip/ramp behind the slab in eye views from the SW. Design read (same as W54): an asphalt apron on fill meets the
# lawn with a graded grass bank, not an exposed slab edge. Paving NOT moved (raise paving, never lower). New object
# WS240_CCOM_apron_S_corner_lawn_bank_UNVERIFIED: 0.2 m lawn grid over exposed ground only (no apron/slab/walk/shoulder hit),
# z = max over covered paving within 2.2 m of (paving z - 0.03 - 0.40*dist) (<= 1:2.5 bank), kept 2 cm under any walk within
# 0.6 m, used only where it rises >= 1.5 cm over the evaluated terrain. No photo of this corner: UNVERIFIED.
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1,ST=5.0,15.0,-45.0,-37.0,0.2
PAV=['CCOM_dock_apron_20261014jf3','WS209_CCOM_walk_apron_crossing_slab_OSM_','WS32_CCOM_apron_east_edge_skirt']
WALK=['Footpaths_OSM','WS206_CCOM_walk_E_edge_straight_fill_ort']
COV=PAV+WALK+['WS226_CCOM_dock_apron_lawn_shoulder_UNVE']
def find(p): return [o for o in bpy.data.objects if o.name.startswith(p) and o.type=='MESH']
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,evalmods):
    sv=[m.show_viewport for m in o.modifiers]
    if evalmods:
        for m in o.modifiers: m.show_viewport=m.show_render
    d=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(d); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
    for m,s in zip(o.modifiers,sv): m.show_viewport=s
    return t
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m'],True)
B={}
for p in COV:
    for o in find(p): B[o.name]=(p,bvh(o,True))
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] else None
nx=int(round((X1-X0)/ST))+1; ny=int(round((Y1-Y0)/ST))+1
G={}; pav=[]; walk=[]
for j in range(ny):
    for i in range(nx):
        x=X0+i*ST; y=Y0+j*ST; tz=hz(T,x,y); cov=None
        for n,(p,t) in B.items():
            z=hz(t,x,y)
            if z is not None and (tz is None or z>tz-0.05):
                cov=(p,z) if cov is None or z>cov[1] else cov
        G[i,j]=(x,y,tz,cov)
        if cov and cov[0] in PAV: pav.append((x,y,cov[1]))
        if cov and cov[0] in WALK: walk.append((x,y,cov[1]))
Z={}; raised=0; maxr=0
for (i,j),(x,y,tz,cov) in G.items():
    if cov or tz is None: continue
    tg=-1e9
    for (px,py,pz) in pav:
        d=math.hypot(px-x,py-y)
        if d<2.2: tg=max(tg,pz-0.03-0.40*d)
    for (wx,wy,wz) in walk:
        if math.hypot(wx-x,wy-y)<0.6: tg=min(tg,wz-0.02)
    if tg>=tz+0.015:
        Z[i,j]=tg; raised+=1; maxr=max(maxr,tg-tz)
    else: Z[i,j]=tz-0.03
bm=bmesh.new(); V={}
def vv(i,j):
    if (i,j) not in V: x,y,tz,c=G[i,j]; V[i,j]=bm.verts.new((x,y,Z[i,j]))
    return V[i,j]
nf=0
for j in range(ny-1):
    for i in range(nx-1):
        q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if not all(k in Z for k in q): continue
        if not any(Z[k]>G[k][2] for k in q): continue
        bm.faces.new([vv(*k) for k in q]); nf+=1
me=bpy.data.meshes.new('WS240_CCOM_apron_S_corner_lawn_bank_UNVERIFIED'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new(me.name,me)
sh=bpy.data.objects.get('WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED')
cols=sh.users_collection if sh else [bpy.context.scene.collection]
cols[0].objects.link(ob)
mat=bpy.data.materials.get('WS70_berm_lawn_ortho_matched') or (sh.data.materials[0] if sh and sh.data.materials else None)
if mat: me.materials.append(mat)
print('F240B pav',len(pav),'walk',len(walk),'raised pts',raised,'max raise',round(maxr,3),'faces',nf,'mat',mat.name if mat else None,'coll',cols[0].name,flush=True)

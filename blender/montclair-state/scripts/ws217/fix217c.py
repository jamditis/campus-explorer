# ws217 W40: between the WS215 walk's N edge (y -46.35) and the stair-tower wall the terrain (WS68 north-DTM ground, tan ortho
# tone) shows as a ragged 0.3-0.6 m strip that stands up to ~0.1 m ABOVE the walk (subset ray probe with terrain GN on). The
# Street View shows the concrete walk running right to the wall. Extend the walk's N-edge columns (x > -263.1) to the wall face
# (horizontal ray vs the core skin, +3 cm into it), keeping their grade; then tuck every WS68 vertex the walk covers 5 cm under it.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
SL=ob('WS215_RHD_SE_core_street_level_sidewalk'); G=ob('WS68_RHD_ground_northDTM')
def bvh(o,top=False):
    M=o.matrix_world; P=[p for p in o.data.polygons if (not top) or (M.to_3x3()@p.normal).z>0.7]
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in P])
SK=[o for o in bpy.data.objects if o.name.startswith(('bx_rhd_se_core_skin','Red Hawk SE core'))]
TK=[bvh(o) for o in SK]
def wally(x,z):
    best=None
    for t in TK:
        h=t.ray_cast(Vector((x,-49.0,z)),Vector((0,1,0)),6)
        if h[0] is not None and (best is None or h[0].y<best): best=h[0].y
    return best
M=SL.matrix_world; Mi=M.inverted(); n=0; dys=[]
for v in SL.data.vertices:
    w=M@v.co
    if w.x>-263.1 and w.y>-46.45:
        yw=wally(w.x,125.6)
        if yw is None or yw<w.y: continue
        dys.append(round(yw+0.03-w.y,3)); v.co=Mi@Vector((w.x,yw+0.03,w.z)); n+=1
SL.data.update()
print('F217c walk N-edge verts moved to wall',n,'dy min/max',min(dys) if dys else None,max(dys) if dys else None,'skins',[o.name[:25] for o in SK],flush=True)
TS=bvh(SL,top=True); Mg=G.matrix_world; Mgi=Mg.inverted(); k=0
for v in G.data.vertices:
    w=Mg@v.co
    if not (-275<w.x<-250 and -56<w.y<-42): continue
    h=TS.ray_cast(Vector((w.x,w.y,200)),Vector((0,0,-1)),300)
    if h[0] is not None and w.z>h[0].z-0.05: v.co=Mgi@Vector((w.x,w.y,h[0].z-0.05)); k+=1
G.data.update()
print('F217c WS68 verts tucked under walk',k,flush=True)

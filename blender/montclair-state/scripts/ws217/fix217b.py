# ws217 W39: Joe's Sep 2021 Street View (refs/joe/red_hawk_deck_college_ave_streetview_sep2021_joe_20261027.png) shows the
# RHD SE stair-tower walk as: concrete curb at College Ave -> a RED BRICK BAND along the back of the curb -> plain concrete walk
# running straight to the building wall (no tan strip at the wall foot). The "brick band at the wall foot" in earlier notes was
# a misread: the band runs along the CURB. (1) add the curb-side brick band (0.15 m curb top kept, band 0.30 m wide, UNVERIFIED
# width by eye ~2 brick lengths), 6 mm proud of the walk; (2) the LI wall-foot gap fill (tan, ragged where the ws216 walk raise
# cut through it) is redundant now that the walk reaches the core face: tuck its verts 1 cm under the walk top where the walk
# covers them (tuck-under covered by a raised surface; AGENTS rule 6 OK).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
SL=ob('WS215_RHD_SE_core_street_level_sidewalk')
def bvh(o,top=False):
    M=o.matrix_world; P=[p for p in o.data.polygons if (not top) or (M.to_3x3()@p.normal).z>0.7]
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in P])
def ray(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
TS=bvh(SL,top=True)
M=SL.matrix_world; W=[M@v.co for v in SL.data.vertices]
# S edge by probing: for each x, lowest y where the walk top exists
def sedge(x):
    y=-54.0
    while y<-46.0:
        if ray(TS,x,y) is not None: return y
        y+=0.02
    return None
xs=[]; x=-266.9
while x<=-255.7: xs.append(round(x,3)); x+=0.25
rows=[]
for x in xs:
    ys=sedge(x)
    if ys is None: continue
    a,b=ys+0.15,ys+0.45
    za,zb=ray(TS,x,a),ray(TS,x,b)
    if za is None or zb is None: continue
    rows.append((x,a,b,za+0.006,zb+0.006))
me=bpy.data.meshes.new('WS217_RHD_SE_curbside_brick_band'); bm=bmesh.new(); prev=None
for x,a,b,za,zb in rows:
    v1=bm.verts.new((x,a,za)); v2=bm.verts.new((x,b,zb))
    if prev: bm.faces.new((prev[0],v1,v2,prev[1]))
    prev=(v1,v2)
bm.to_mesh(me); bm.free()
BR=bpy.data.materials.get('WS3_Brick_soldier_course')
if BR is None:
    with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (fd,td): td.materials=['WS3_Brick_soldier_course']
    BR=bpy.data.materials.get('WS3_Brick_soldier_course')
me.materials.append(BR)
o=bpy.data.objects.new('WS217_RHD_SE_curbside_brick_band_streetview2021_UNVERIFIED_width',me)
for c in SL.users_collection: c.objects.link(o)
print('F217b brick band rows',len(rows),'x',rows[0][0] if rows else None,rows[-1][0] if rows else None,'mat',BR.name if BR else None,flush=True)
GF=ob('LI_rhd_se_wall_foot_gap_fill'); n=0
if GF:
    Mg=GF.matrix_world; Mgi=Mg.inverted()
    for v in GF.data.vertices:
        w=Mg@v.co; z=ray(TS,w.x,w.y)
        if z is not None and w.z>z-0.01: v.co=Mgi@Vector((w.x,w.y,z-0.01)); n+=1
    GF.data.update()
print('F217b gap-fill verts tucked under walk',n,'of',len(GF.data.vertices) if GF else 0,flush=True)

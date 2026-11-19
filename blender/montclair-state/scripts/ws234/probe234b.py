# ws234 read-only: seat check of the M2b station/rail batch in main ws234a. Appends only the new objects + main's ground
# objects (Context_skirt_3DEP_ortho_4km, Terrain_LiDAR_DTM_1m, WS60 apron, WF patch), modifiers off (raw ground), and casts
# vertical rays at sampled vertices of ballast / platforms / stair feet. Reports clearance = object bottom - ground.
import bpy, json, os, mathutils, random
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
F=os.environ.get('FILE',MS+'montclair_state_ws234a.blend')
new=json.load(open(MS+'scripts/ws234/m2b_new234.json'))+json.load(open(MS+'scripts/ws234/cc_names234.json'))
G=[os.environ.get('EXT','M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam'),'Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in new+G if n in set(a.objects)]
for o in b.objects:
    if o: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects.get(n)
    if not o: return None
    m=o.data.copy(); m.transform(o.matrix_world); return BVHTree.FromPolygons([v.co[:] for v in m.vertices],[p.vertices[:] for p in m.polygons])
T={n:bvh(n) for n in G}
def ground(x,y):
    hs=[]
    for n,t in T.items():
        if not t: continue
        h=t.ray_cast(mathutils.Vector((x,y,400)),mathutils.Vector((0,0,-1)))
        if h[0]: hs.append((h[0].z,n))
    return max(hs) if hs else (None,None)
random.seed(1); rep={}
for n in new:
    o=bpy.data.objects.get(n)
    if not o or o.type!='MESH' or not any(k in n for k in ('Ballast','Platform','platform','stair','Stair','landing','MH Rail ties','fence','Children')): continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    if not vs: continue
    # bottom verts: per xy cell the lowest
    cells={}
    for v in vs:
        k=(round(v.x/3),round(v.y/3))
        if k not in cells or v.z<cells[k].z: cells[k]=v
    samp=list(cells.values()); random.shuffle(samp); samp=samp[:400]
    d=[];src={}
    for v in samp:
        g,gn=ground(v.x,v.y)
        if g is None: continue
        d.append(v.z-g); src[gn]=src.get(gn,0)+1
    if d:
        d.sort(); rep[n]=dict(n=len(d),min=round(d[0],2),med=round(d[len(d)//2],2),max=round(d[-1],2),buried_gt0p3=sum(1 for x in d if x<-0.3),float_gt0p5=sum(1 for x in d if x>0.5),src=src)
        print('P234B',n[:60],rep[n],flush=True)
json.dump(rep,open(MS+''+os.environ.get('REP','scripts/ws234/probe234b.json')+'','w'),indent=0)

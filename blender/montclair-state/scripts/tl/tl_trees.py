# tl (Nov 4 2026 ~9:45 PM ET, MAIN): trees round the east dorms (Stone/Blanton/Bohn, Webster lawn edges) at LiDAR tree tops
# (data/tl/dorm_tree_tops.json from scripts/tl/tl_tree_tops.py: 2017 B17 J5D6 1 m CHM local maxima >= 4 m).
# Positions + heights from LiDAR (approx +-1 m); species/model = existing Trees_assets_LiDAR meshes (shared data), UNVERIFIED.
# Skips: OSM buildings +2 m, Webster site +6 m (demolished 2025, kept as lawn per Joe), modelled roads/lots/walks (ray hit not ground), existing trees < 4 m.
import bpy, json, math, os, random
from mathutils import Vector, Matrix
REV=os.environ.get('REVERT')=='1'
def revert():
    for o in [o for o in bpy.data.objects if 'tl_tree' in o]: bpy.data.objects.remove(o)
    c=bpy.data.collections.get('TL_dorm_trees_LiDAR_UNVERIFIED')
    if c: bpy.data.collections.remove(c)
    print('TLT reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
# building/Webster filter precomputed with shapely (system python) -> data/tl/dorm_tree_tops_filtered.json
T=json.load(open('data/tl/dorm_tree_tops_filtered.json'))
src=[o for o in bpy.data.collections['Trees_assets_LiDAR'].all_objects if o.type=='MESH']
meshes={}
for o in src: meshes.setdefault(o.data.name,o)
info=[]
for n,o in meshes.items():
    zs=[v.co.z for v in o.data.vertices]; h=max(zs)-min(zs); info.append((n,min(zs),h,o.data.materials[0].name if o.data.materials else ''))
print('TLT meshes',[(i[0],round(i[2],1)) for i in info])
ex=[o.matrix_world.translation.copy() for o in src]
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
GN={'Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED'}
def hit(x,y):
    r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    return r
col=bpy.data.collections.new('TL_dorm_trees_LiDAR_UNVERIFIED'); sc.collection.children.link(col)
rng=random.Random(20261104); made=0; sk={'bld':0,'near':0,'nohit':0,'notground':0}
skipnames={}
for x,y,gzl,h,cr in T:
    if any((Vector((x,y,0))-Vector((e.x,e.y,0))).length<4 for e in ex): sk['near']+=1; continue
    # ground under the trunk: walk down through grass/point objects
    r=hit(x,y)
    if not r[0]: sk['nohit']+=1; continue
    o=r[4]; nm=o.name
    if nm not in GN and not any(k in nm.lower() for k in ('ground','terrain','lawn','grass','skirt','drape')):
        sk['notground']+=1; skipnames[nm]=skipnames.get(nm,0)+1; continue
    z=r[1].z
    h=(gzl+h)-z  # tree-top elevation from LiDAR, height over the scene ground (handles DTM hole fill on the east slope)
    if not (4.0<=h<=26.0) or gzl+h<z: sk['height']=sk.get('height',0)+1; continue
    n,zmin,mh,mat=info[rng.randrange(len(info))]
    s=max(0.45,min(2.2,h/mh))
    ob=bpy.data.objects.new('TL_tree_%03d_UNVERIFIED'%made,meshes[n].data); col.objects.link(ob); ob['tl_tree']=1
    ob['UNVERIFIED']='LiDAR 2017 tree top (x,y,h=%.1f m); species/model approximated'%h
    ob.matrix_world=Matrix.Translation((x,y,z-0.25-zmin*s))@Matrix.Rotation(rng.uniform(0,2*math.pi),4,'Z')@Matrix.Diagonal((s,s,s*rng.uniform(0.95,1.05),1))
    made+=1
print('TLT trees',made,'skipped',sk,'notground hits',sorted(skipnames.items(),key=lambda t:-t[1])[:12])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')

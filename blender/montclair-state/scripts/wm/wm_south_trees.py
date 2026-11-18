"""wm pass 2: LiDAR-CHM trees on the coarse skirt south/west of the WJ ext where OSM wood + 2017 canopy say woodland (x150-245, y228-292),
seated by lowest point on the rendered skirt (evaluated), heights from 2017 DSM-DTM (capped 26 m), same assets/method as wj_trees.py."""
import bpy, json, math, random, numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
SK=bvh('Context_skirt_3DEP_ortho_4km'); PT=[bvh('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'),bvh('WJ_south_gully_LiDAR_patch_ext_UNVERIFIED')]
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
z=np.load(f'{ROOT}/data/wm/litter_mask_wm.npz'); M=z['m_pre_trees']
g=np.load(f'{ROOT}/data/wm/chm_grid_south_1m.npz'); kd=[f for f in g.files if 'J5D6' in f and f.endswith('dtm')][0]
D=g[kd]; S=g[kd.replace('dtm','dsm')]; H=np.nan_to_num(S-D,nan=0.0)
P=np.pad(H,1,mode='edge');Hs=sum(P[a:a+H.shape[0],b:b+H.shape[1]] for a in range(3) for b in range(3))/9
P2=np.pad(Hs,2,mode='edge');mx=np.max(np.stack([P2[a:a+H.shape[0],b:b+H.shape[1]] for a in range(5) for b in range(5)]),axis=0)
tops=[]
for j,i in zip(*np.where((Hs>=mx-1e-9)&(Hs>=4))):
    x=120+i+0.5; y=215+j+0.5
    if not(150<=x<=245 and 228<=y<=292): continue
    mi=M[int(y-215),int(x-120)]
    if mi<0.3: continue
    tops.append((x,y,float(Hs[j,i]+(H[j,i]-Hs[j,i])*0.5)))
src=[o for o in bpy.data.collections['Trees_assets_LiDAR'].all_objects if o.type=='MESH']
meshes={}
for o in src: meshes.setdefault(o.data.name,o)
info=[(n,min(v.co.z for v in o.data.vertices),max(v.co.z for v in o.data.vertices)-min(v.co.z for v in o.data.vertices)) for n,o in meshes.items()]
ex=[o.matrix_world.translation.copy() for o in bpy.data.objects if o.name.startswith(('TL_tree_','WJ_gully_tree_')) or o in src]
col=bpy.data.collections.get('TL_dorm_trees_LiDAR_UNVERIFIED')
rng=random.Random(20261108); k=0; rep={'added':[]}
for x,y,h in sorted(tops):
    if any(math.hypot(e.x-x,e.y-y)<4.5 for e in ex): continue
    if any(hz(b,x,y) is not None for b in PT): continue   # LiDAR patches have their own trees
    zg=hz(SK,x,y)
    if zg is None: continue
    hh=min(26.0,h)
    n,zmin,mh=info[rng.randrange(len(info))]; s=max(0.45,min(2.2,hh/mh))
    ob=bpy.data.objects.new('WM_south_wood_tree_%02d_UNVERIFIED'%k,meshes[n].data); col.objects.link(ob)
    ob['wm_tree']=1; ob['UNVERIFIED']='wm: 2017 LiDAR CHM top south of the WJ ext (h=%.1f m, capped 26), seated on the 3DEP skirt; species/model approximated; OSM natural=wood 315835594'%hh
    ob.matrix_world=Matrix.Translation((x,y,zg-0.25-zmin*s))@Matrix.Rotation(rng.uniform(0,2*math.pi),4,'Z')@Matrix.Diagonal((s,s,s*rng.uniform(0.95,1.05),1))
    ex.append(Vector((x,y,0))); rep['added'].append([ob.name,round(x,1),round(y,1),round(hh,1)]); k+=1
rep['n_tops']=len(tops); rep['n_added']=k
print('TREES',rep['n_tops'],k)
json.dump(rep,open(f'{ROOT}/data/wm/south_trees_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED')

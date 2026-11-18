"""wj trees: (a) reseat TL trees on WF/WJ patches by lowest point (bbox min) = ground-0.25; (b) add LiDAR-top trees in the south gully ext (y292-320, x182-258), same method as tl_trees.py."""
import bpy, json, math, random, numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
ROOT='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
BP=[bvh('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'),bvh('WJ_south_gully_LiDAR_patch_ext_UNVERIFIED')]
def pz(x,y):
    hs=[h[0].z for h in [b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for b in BP] if h[0] is not None]; return max(hs) if hs else None
rep={'reseat':[], 'added':[]}
# (a)
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree_'): continue
    t=o.matrix_world.translation; g=pz(t.x,t.y)
    if g is None: continue
    bb=min((o.matrix_world@Vector(c)).z for c in o.bound_box)
    dz=(g-0.25)-bb
    if abs(dz)>0.15:
        o.location.z+=dz; o['wj_dz2']=float(dz); rep['reseat'].append([o.name,round(dz,2)])
# (b) CHM tops
g=np.load(f'{ROOT}/data/wj/south_hollow_grid_1m.npz');kd=[f for f in g.files if 'B17_J5D6' in f and 'dtm' in f][0]
D=g[kd];S=g[kd.replace('dtm','dsm')];H=np.nan_to_num(S-D,nan=0.0)
P=np.pad(H,1,mode='edge');Hs=sum(P[a:a+H.shape[0],b:b+H.shape[1]] for a in range(3) for b in range(3))/9
P2=np.pad(Hs,2,mode='edge');mx=np.max(np.stack([P2[a:a+H.shape[0],b:b+H.shape[1]] for a in range(5) for b in range(5)]),axis=0)
tops=[]
for j,i in zip(*np.where((Hs>=mx-1e-9)&(Hs>=4))):
    x=150+i+0.5;y=290+j+0.5
    if 182<=x<=258 and 292<=y<320: tops.append((x,y,float(D[j,i]) if np.isfinite(D[j,i]) else None,float(Hs[j,i]+ (H[j,i]-Hs[j,i])*0.5)))
src=[o for o in bpy.data.collections['Trees_assets_LiDAR'].all_objects if o.type=='MESH']
meshes={}
for o in src: meshes.setdefault(o.data.name,o)
info=[]
for n,o in meshes.items():
    zs=[v.co.z for v in o.data.vertices]; info.append((n,min(zs),max(zs)-min(zs)))
ex=[o.matrix_world.translation.copy() for o in bpy.data.objects if o.name.startswith('TL_tree_') or o in src]
col=bpy.data.collections.get('TL_dorm_trees_LiDAR_UNVERIFIED')
rng=random.Random(20261107); k=0
for x,y,gl,h in sorted(tops):
    if any(math.hypot(e.x-x,e.y-y)<4 for e in ex): continue
    z=pz(x,y)
    if z is None or gl is None: continue
    top=gl+h; hh=min(26.0,top-z)
    if hh<4: continue
    n,zmin,mh=info[rng.randrange(len(info))]; s=max(0.45,min(2.2,hh/mh))
    ob=bpy.data.objects.new('WJ_gully_tree_%02d_UNVERIFIED'%k,meshes[n].data); col.objects.link(ob)
    ob['wj_tree']=1; ob['UNVERIFIED']='wj: 2017 LiDAR CHM top in south gully (h=%.1f m, capped 26); species/model approximated; OSM natural=wood 315835594'%hh
    ob.matrix_world=Matrix.Translation((x,y,z-0.25-zmin*s))@Matrix.Rotation(rng.uniform(0,2*math.pi),4,'Z')@Matrix.Diagonal((s,s,s*rng.uniform(0.95,1.05),1))
    ex.append(Vector((x,y,0))); rep['added'].append([ob.name,x,y,round(hh,1)]); k+=1
rep['n_tops']=len(tops); rep['n_reseat']=len(rep['reseat']); rep['n_added']=k
print('TREES',json.dumps({k_:v for k_,v in rep.items() if k_ not in('reseat',)})); print('RESEAT',rep['reseat'])
json.dump(rep,open(f'{ROOT}/data/wj/trees_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile()

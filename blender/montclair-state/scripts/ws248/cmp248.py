# ws248: model terrain (raw + evaluated) vs 2023/2017 LiDAR ground around the east stand
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws248a.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','fs_turf','fse_stand_under_pad']
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T=b.objects[0]
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); box=(-262,-198,38,172)
def bvh(o,ev=True):
    me=o.evaluated_get(dg).to_mesh() if ev else o.data; M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps)
TE=bvh(T); TR=bvh(T,False); TU=bvh(b.objects[1])
print('CMP248 mods',[ (m.name,m.show_viewport) for m in T.modifiers][:60],flush=True)
L=np.load('/workspace/nj-scenes/montclair-state/scripts/ws248/las248.npy'); g=L[L[:,3]==2]
L7=np.load('/workspace/nj-scenes/montclair-state/scripts/ws248/las248_2017.npy'); g7=L7[L7[:,3]==2]
def z(t,x,y):
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return None if h[0] is None else round(h[0].z,2)
def lz(g,x,y,r=1.0):
    m=(abs(g[:,0]-x)<r)&(abs(g[:,1]-y)<r); return round(float(np.median(g[m,2])),2) if m.sum()>2 else None
for y in range(50,170,10):
    row=[]
    for x in (-250,-240,-230,-222,-216,-210,-204):
        row.append('%d:%s/%s|%s/%s'%(x,z(TR,x,y),z(TE,x,y),lz(g,x,y),lz(g7,x,y)))
    print('CMP248 y',y,' '.join(row),flush=True)
print('CMP248 turf z at (-245,110)',z(TU,-245,110),flush=True)
sys.stdout.flush(); os._exit(0)

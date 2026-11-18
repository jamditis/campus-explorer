import bpy, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bt=BVHTree.FromObject(T,dg)
bs=BVHTree.FromObject(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],dg)
D=np.load('north/data/grid_1m.npz')['dtm_filled']
miss=[];dev=[];pk=[]
for y in np.arange(-34.5,250,1.0):
    for x in np.arange(150.5,246,1.0):
        h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; s=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if h is None:
            if s is not None: miss.append((x,y))
            continue
        if x<219: dev.append((abs(h.z-D[int(math.floor(y))+260,int(math.floor(x))+600]),x,y))
        if s is not None and s.z>h.z-0.005: pk.append((round(s.z-h.z,2),x,y))
dev.sort(reverse=True)
print('VERIFY skirt-visible cells (terrain miss)',len(miss),'| dev>1m',sum(1 for d in dev if d[0]>1),'max',[(round(a,2),b,c) for a,b,c in dev[:5]])
pk.sort(reverse=True); print('VERIFY skirt pokes',len(pk),pk[:8])
# holes along old boundary: compare miss set with pre (env)
import json; json.dump(miss,open('/tmp/qi_miss_%s.json'%bpy.path.basename(bpy.data.filepath),'w'))
fl=[]
for o in bpy.data.objects:
    if not o.name.startswith(('T_','Lamp','Bench')) or o.hide_render or o.parent: continue
    x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
    if not(140<=x<=250 and -40<=y<=255): continue
    zmin=min((o.matrix_world@Vector(c)).z for c in o.bound_box); h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
    if h is None: fl.append((o.name,'nohit')); continue
    if abs(zmin-h.z)>0.4: fl.append((o.name,round(zmin-h.z,2),round(o.matrix_world.translation.z-h.z,2)))
print('VERIFY float/buried',len(fl),fl[:30])

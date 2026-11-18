import bpy, numpy as np, collections
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
X0,X1,Y0,Y1=[float(v) for v in __import__('os').environ['BOX'].split(',')]
res=collections.defaultdict(list)
for x in np.arange(X0,X1,1.0):
    for y in np.arange(Y0,Y1,1.0):
        h=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        if not h[0] or h[4]==ter: continue
        o=h[4]; z=h[1].z
        # terrain below
        p=Vector((x,y,z-0.001)); zt=None
        for _ in range(6):
            g=sc.ray_cast(dg,p,Vector((0,0,-1)))
            if not g[0]: break
            if g[4]==ter: zt=g[1].z; break
            p=g[1]-Vector((0,0,0.001))
        if zt is None: continue
        d=z-zt
        if d>0.25 and o.dimensions.z<4: res[o.name].append((float(x),float(y),round(d,2)))
for k,v in sorted(res.items(),key=lambda kv:-len(kv[1])):
    ds=[t[2] for t in v]; print('FLOAT',k[:60],len(v),'max',max(ds),'xs',min(t[0] for t in v),max(t[0] for t in v),'ys',min(t[1] for t in v),max(t[1] for t in v))

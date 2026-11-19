import bpy
from collections import Counter
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for o in [o for o in bpy.data.objects if o.name.startswith('WS215_RHD_SE_core_street_level_sidewalk')]:
    M=o.matrix_world; c=Counter()
    for p in o.data.polygons:
        for k in p.edge_keys: c[k]+=1
    bed=[k for k,n in c.items() if n==1]
    bset=set(); [bset.update(k) for k in bed]
    print('P222 OBJ',o.name,len(o.data.vertices),len(o.data.polygons))
    for i in sorted(bset,key=lambda i:(M@o.data.vertices[i].co).x):
        w=M@o.data.vertices[i].co
        if -257.2<=w.x<=-255.3 and -53.6<=w.y<=-52.0 and w.z>124.9:
            nb=[k for k in bed if i in k]
            print('P222  v%d (%.3f,%.3f,%.3f) nb %s'%(i,w.x,w.y,w.z,[k[0] if k[1]==i else k[1] for k in nb]))
# curb front line points
for x in (-255.5,-255.8,-256.1,-256.4,-256.7):
    y=-53.040+(-0.526)*(x+255.418)
    h=sc.ray_cast(dg,Vector((x,y-0.05,127)),Vector((0,0,-1)))
    print('P222 line x %.2f y %.3f below-road hit %s %.3f'%(x,y,h[4].name[:20] if h[0] else '-',h[1].z if h[0] else 0))

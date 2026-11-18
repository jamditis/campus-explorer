import bpy,numpy as np,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
pre=tuple(os.environ.get('SLP','QS_footway_,QW_footway_,QS_service_,TR_footway,SG_').split(','))
names=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(pre)]; B={n:bvh(O[n]) for n in names}; gn=os.environ['G']; Gb=bvh(O[gn])
for pt in os.environ['PTS'].split(';'):
    x,y=map(float,pt.split(','))
    g=Gb.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
    res=[]
    for n,b in B.items():
        for r in np.arange(0.1,0.46,0.1):
            for a in np.linspace(0,2*np.pi,16,endpoint=False):
                h=b.ray_cast(Vector((x+r*np.cos(a),y+r*np.sin(a),500)),Vector((0,0,-1)))[0]
                if h: res.append((round(h.z-g.z,3),n[:30],round(r,1)))
    res.sort(reverse=True); print('PT',x,y,'g',round(g.z,2),res[:3],flush=True)

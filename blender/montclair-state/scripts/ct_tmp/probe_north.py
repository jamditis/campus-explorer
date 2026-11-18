import bpy, numpy as np
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def cam_rays(L,T,lens,pix):
    L=Vector(L);T=Vector(T); q=(T-L).normalized().to_track_quat('-Z','Y'); fx=36/lens; fy=fx*720/1280
    for px,py in pix:
        r=(q@Vector(((px/1280-0.5)*fx,(0.5-py/720)*fy,-1))).normalized()
        h,l,n,i,o,m=sc.ray_cast(dg,L,r)
        print('PX',px,py,(o.name[:55] if o else None),tuple(round(c,2) for c in l) if h else None, flush=True)
pix=[(x,y) for y in range(600,720,12) for x in range(720,820,8)]
cam_rays((-222.0,-128.0,162.0),(-186.0,-74.0,130.0),30,pix)
# north ground under the new terrace (s/u frame)
A=np.array([-250.1,-46.7]);B=np.array([-237.3,3.8]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
ter=[o for o in bpy.data.objects if o.type=='MESH' and not o.library and ('terrain' in o.name.lower() or 'skirt' in o.name.lower() or 'grass' in o.name.lower() or 'lawn' in o.name.lower())]
print('ground objs',[o.name for o in ter])
from mathutils.bvhtree import BVHTree
import bmesh
for o in ter:
    if len(o.data.polygons)==0: continue
    b=bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free()
    zs=[]
    for s in np.arange(61,70.5,0.5):
        for u in np.arange(2.3,12.5,0.5):
            p=A+n*s+d*u; h=t.ray_cast(Vector((p[0],p[1],160)),Vector((0,0,-1)))
            if h[0] is not None: zs.append(h[0].z)
    if zs: print('GROUND',o.name,len(zs),'max',round(max(zs),2),'p50',round(float(np.median(zs)),2))

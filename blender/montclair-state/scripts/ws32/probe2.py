import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); e.to_mesh_clear()
    return BVHTree.FromBMesh(b), b
FP,fb=bvh('Footpaths_OSM'); AP,ab=bvh('CCOM_dock_apron_20261014jf3')
print('apron faces',len(ab.faces),'verts',len(ab.verts))
import collections
hist=collections.Counter(); pts=[]
for x10 in range(-30,152,5):
  for y10 in range(-392,-210,5):
    x=x10/10; y=y10/10
    a=AP.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),30); f=FP.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),30)
    if a[0] and f[0]:
        d=f[0].z-a[0].z; hist[round(d,2) if abs(d)<0.1 else ('>' if d>0 else '<')]+=1; pts.append((x,y,d))
print('overlap samples',len(pts))
print(sorted(hist.items(),key=lambda k:str(k[0])))
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
if pts: print('overlap bbox',min(xs),max(xs),min(ys),max(ys))
# grid map of sign
for y10 in range(-392,-210,10):
    s=''
    for x10 in range(-30,152,5):
        x=x10/10;y=y10/10
        a=AP.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),30); f=FP.ray_cast(Vector((x,y,150)),Vector((0,0,-1)),30)
        if a[0] and f[0]:
            d=f[0].z-a[0].z; s+= '+' if d>0.02 else ('-' if d<-0.02 else '=')
        elif a[0]: s+='a'
        elif f[0]: s+='f'
        else: s+='.'
    print(f'{y10/10:6.1f} {s}')
for m in bpy.data.objects['Footpaths_OSM'].data.materials: print('FPMAT',m.name)

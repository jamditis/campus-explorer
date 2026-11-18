import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
fr=[o for o in bpy.data.objects if o.name.startswith('TX Partridge precast frame')][0]
core=[o for o in bpy.data.objects if o.name.startswith('TX Partridge core')][0]
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); mats=[f.material_index for f in bm.faces]
    t=BVHTree.FromBMesh(bm); bm.free(); return t,mats
FT,FM=bvh(fr)
print('slots',[s.material.name for s in fr.material_slots])
for i,p in enumerate(core.data.polygons):
    if abs(p.normal.z)>0.1: continue
    vs=[core.matrix_world@core.data.vertices[k].co for k in p.vertices]
    n=(core.matrix_world.to_3x3()@p.normal).normalized()
    zs=[v.z for v in vs]; xy=sorted(vs,key=lambda v:v.z)
    a=[v for v in vs if abs(v.z-min(zs))<0.01]
    if len(a)<2: continue
    A,B=a[0],a[1]; t=(B-A); t.z=0; W=t.length; t.normalize()
    print('FACE',i,'n',tuple(round(c,2) for c in n),'A',tuple(round(c,2) for c in A),'W',round(W,2),'z',round(min(zs),2),round(max(zs),2))
    rows=[]
    z=139.0
    while z<155.4:
        r=''
        s=0.2
        while s<W-0.1:
            o=A+t*s; o.z=z; st=o+n*2.0
            h=FT.ray_cast(st,-n,2.6)
            if h[0] is None: r+='.'
            else:
                m=FM[h[2]]; r+= {0:'#',1:'g',2:'#',3:'|'}.get(m,'?')
            s+=0.4
        rows.append(r); z+=0.5
    for r in reversed(rows): print('  ',r)

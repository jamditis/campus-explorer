import bpy,bmesh,os
from mathutils import Vector
import numpy as np
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
uvl=bm.loops.layers.uv['facade']
print('faces',len(bm.faces),'verts',len(bm.verts))
bad=[]
allres=[]
for f in bm.faces:
    n=(M.to_3x3()@f.normal); n.z=0
    if n.length<0.5: continue
    n.normalize(); t=Vector((-n.y,n.x,0))
    P=[M@l.vert.co for l in f.loops]; U=[l[uvl].uv.x for l in f.loops]; Vv=[l[uvl].uv.y for l in f.loops]
    s=np.array([p.dot(t) for p in P]); z=np.array([p.z for p in P]); U=np.array(U); Vv=np.array(Vv)
    # expected du = +-ds ; check consistency
    a1=np.std((U - s)); a2=np.std((U + s)); res=min(a1,a2)
    rv=np.std(Vv-z)
    allres.append(res)
    c=sum(P,Vector())/len(P)
    if res>0.05 or rv>0.05: bad.append((round(c.x,1),round(c.y,1),round(c.z,1),len(P),round(res,2),round(rv,2),round(max(z)-min(z),2)))
print('BAD',len(bad))
for b in sorted(bad,key=lambda b:-b[4])[:60]: print('B',b)

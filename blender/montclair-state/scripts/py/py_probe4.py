import bpy, collections
from mathutils import Vector
from mathutils.kdtree import KDTree
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5
el=[o for o in bpy.data.objects if o.name.startswith('el coping strips Dickson')][0]
E=[el.matrix_world@v.co for v in el.data.vertices]
print('ELZ',sorted(collections.Counter(round(c.z,2) for c in E if inwing(c)).items()))
kd=KDTree(len(E))
for i,c in enumerate(E): kd.insert(Vector((c.x,c.y,0)),i)
kd.balance()
for on in ('Dickson Hall walls','PX_Dickson_wing_parapet_infill_UNVERIFIED'):
    o=bpy.data.objects[on]; me=o.data; W=[o.matrix_world@v.co for v in me.vertices]
    ec=collections.Counter()
    for p in me.polygons:
        for k in p.edge_keys: ec[k]+=1
    D=[]
    for k,c in ec.items():
        if c!=1: continue
        a=W[k[0]]; b=W[k[1]]; m=(a+b)/2
        if not inwing(m) or min(a.z,b.z)<150.4 or (a.xy-b.xy).length<0.05: continue
        co,i,d=kd.find(Vector((m.x,m.y,0))); D.append((round(d,2),round(m.x,1),round(m.y,1),round(m.z,2)))
    D.sort(); print('TOP2EL',on,len(D),'d pct',[D[int(len(D)*q)][0] for q in (0,0.25,0.5,0.75,0.95)] if D else None,'far',[x for x in D if x[0]>0.6][:30])

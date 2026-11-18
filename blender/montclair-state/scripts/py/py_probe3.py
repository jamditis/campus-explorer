import bpy, collections
from mathutils import Vector
from mathutils.kdtree import KDTree
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5
r=bpy.data.objects['Dickson Hall roof (LiDAR)']; me=r.data; mw=r.matrix_world
fm=collections.Counter()
for p in me.polygons:
    c=mw@p.center; n=(mw.to_3x3()@p.normal).normalized()
    if inwing(c): fm[(me.materials[p.material_index].name, 'H' if abs(n.z)>0.7 else 'V', round(c.z))]+=1
print('RFM',sorted(fm.items()))
w=bpy.data.objects['Dickson Hall walls']; WV=[w.matrix_world@v.co for v in w.data.vertices]
kd=KDTree(len(WV))
for i,c in enumerate(WV): kd.insert(Vector((c.x,c.y,0)),i)
kd.balance()
# roof verts at 152.51 in wing: distance to nearest wall vertex (xy)
ds=[]
for v in me.vertices:
    c=mw@v.co
    if inwing(c) and c.z>152.4:
        co,i,d=kd.find(Vector((c.x,c.y,0))); ds.append(d)
ds.sort(); print('ROOF2WALL d pct',[round(ds[int(len(ds)*q)],2) for q in (0.0,0.05,0.25,0.5)] if ds else None, len(ds))
# skirt verts low
lo=[mw@v.co for v in me.vertices if inwing(mw@v.co) and mw@v.co.z<152.4] if False else [c for c in (mw@v.co for v in me.vertices) if inwing(c) and c.z<152.4]
print('ROOFLOW',len(lo),sorted(collections.Counter(round(c.z,1) for c in lo).items())[:20])
dl=[]
for c in lo:
    co,i,d=kd.find(Vector((c.x,c.y,0))); dl.append(d)
dl.sort(); print('LOW2WALL',[round(dl[int(len(dl)*q)],2) for q in (0,0.25,0.5,0.75,0.99)] if dl else None)
el=[o for o in bpy.data.objects if o.name.startswith('el coping strips Dickson')][0]
E=[el.matrix_world@v.co for v in el.data.vertices]; print('EL near wing',len([c for c in E if inwing(c)]))
# el polygon sample dims
p=el.data.polygons[0]; vs=[el.matrix_world@el.data.vertices[i].co for i in p.vertices]; print('ELP0',[tuple(round(x,2) for x in v) for v in vs])
p=el.data.polygons[1]; vs=[el.matrix_world@el.data.vertices[i].co for i in p.vertices]; print('ELP1',[tuple(round(x,2) for x in v) for v in vs])
print('ELSRC',dict(el.items()).get('source_note'))

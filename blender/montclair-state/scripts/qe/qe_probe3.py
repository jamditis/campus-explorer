import bpy, math
from mathutils import Vector
R=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; mw=R.matrix_world
fs=[p for p in R.data.polygons if p.material_index==3]
print('NF',len(fs), 'tot area',round(sum(p.area for p in fs),1))
bins={}
for p in fs:
    n=(mw.to_3x3()@p.normal); a=round(math.degrees(math.atan2(n.y,n.x))/15)*15 if abs(n.z)<0.7 else 'flat'
    c=mw@p.center; bins.setdefault(a,[]).append((p.area,c))
for k,v in sorted(bins.items(),key=lambda kv:-sum(x[0] for x in kv[1])):
    A=sum(x[0] for x in v); cs=[x[1] for x in v]
    print('BIN',k,round(A,1),len(v),'x',round(min(c.x for c in cs),1),round(max(c.x for c in cs),1),'y',round(min(c.y for c in cs),1),round(max(c.y for c in cs),1),'z',round(min(c.z for c in cs),1),round(max(c.z for c in cs),1))

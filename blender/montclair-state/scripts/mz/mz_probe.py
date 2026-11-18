import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def ut(p): return (round(d.dot(p),2), round(n.dot(p)-C0-T0,2), round(p.z,2))
for cn in ('MS_CCOM_newsroom_studio_20261029mw','MS_CCOM_newsroom_studio_detail_20261030mx','MS_CCOM_newsroom_studio_detail2_20261030my'):
    c=bpy.data.collections[cn]; print("==",cn)
    for o in c.all_objects:
        if o.type!='MESH' or len(o.data.vertices)==0: print(o.name,o.type,o.hide_render); continue
        ps=[o.matrix_world@v.co for v in o.data.vertices]
        U=[d.dot(p) for p in ps]; T=[n.dot(p)-C0-T0 for p in ps]; Z=[p.z for p in ps]
        print("%-60s v%5d u %.2f..%.2f t %.2f..%.2f z %.2f..%.2f hr%d mats %s"%(o.name[:60],len(ps),min(U),max(U),min(T),max(T),min(Z),max(Z),o.hide_render,[m.name[:30] for m in o.data.materials]))
gl=bpy.data.materials.get('CCOM_atrium_glass_interior'); print("glassmat users", gl.users if gl else None)

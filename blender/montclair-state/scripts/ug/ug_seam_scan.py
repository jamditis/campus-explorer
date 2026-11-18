import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
def mk(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted(); d=(iw.to_3x3()@Vector((0,0,-1))).normalized()
    def f(x,y):
        r=e.ray_cast(iw@Vector((x,y,400)),d); return round((mw@r[1]).z,2) if r[0] else None
    return f
T=mk('Terrain_LiDAR_DTM_1m'); S=mk('SA_ground_lower_patch_UNVERIFIED')
sc=bpy.context.scene
res=[]
for x in range(-400,400,2):
    t=T(x+.5,249.5); s=S(x+.5,249.5)
    r=sc.ray_cast(dg,Vector((x+.5,249.5,250)),Vector((0,0,-1)))
    res.append(dict(x=x,dtm=t,sa=s,top=(round(r[1].z,2),r[4].name[:48]) if r[0] else None,dtm_s=T(x+.5,246.5),dtm_n=T(x+.5,252.5) or S(x+.5,252.5)))
json.dump(res,open('data/ug/dtm_seam_scan_y249.json','w'),indent=0)
gaps=[d['x'] for d in res if d['dtm'] is None and d['sa'] is None]
print('UGSCAN gaps',len(gaps),gaps[:3],gaps[-3:])

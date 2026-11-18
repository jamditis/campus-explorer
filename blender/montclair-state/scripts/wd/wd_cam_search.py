import bpy, json, math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
e=Vector((0.9444,-0.3291,0)).normalized(); nrm=Vector((-e.y,e.x,0)); M=Vector((226.825,413.425,0)); zL=132.45
def W(s,l,z=0): return Vector((M.x+e.x*s+nrm.x*l, M.y+e.y*s+nrm.y*l, z))
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
def gz(p):
    r=sk.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
    return r[1].z if r[0] else 134
tg=[W(s,l,zL+(0.3 if s>=0 else 0.3+(-s)*0.48)) for s in (-3.5,-2,-0.8,0.8,2.5) for l in (-0.4,0.4)]
res=[]
for s in range(-14,14,2):
    for l in range(2,16,2):
        for dz in (1.7,4.0,7.0):
            c=W(s,l); g=gz(c)
            if g>150: continue
            c.z=g+dz
            # camera must not be inside a mesh: ray up hit?
            ok=0
            for t in tg:
                d=(t-c); r=sc.ray_cast(dg,c,d.normalized(),distance=d.length+0.3)
                if r[0] and r[4].name.startswith(('WD_','TK_Bohn_landing')): ok+=1
            res.append((ok,s,l,dz,round(c.x,1),round(c.y,1),round(c.z,1)))
res.sort(reverse=True); print('BEST',res[:15])
json.dump(res[:40],open('data/wd/cam_search.json','w'))

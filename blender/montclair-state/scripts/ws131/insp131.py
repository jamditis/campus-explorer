import bpy, mathutils
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
sc=bpy.context.scene
print('OBJS in x-186..-160,y-266..-214:')
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.vertices: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    if x1>-186 and x0<-160 and y1>-266 and y0<-214 and (x1-x0)<400:
        print(' ',o.name,len(o.data.polygons),'%.1f %.1f %.1f %.1f z%.1f-%.1f'%(x0,x1,y0,y1,min(v.z for v in bb),max(v.z for v in bb)),'hide' if o.hide_render else '')
def ray(x,y):
    out=[];o=Vector((x,y,200));
    for i in range(4):
        r=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not r[0]: break
        out.append('%s@%.2f'%(r[4].name[:40],r[1].z)); o=r[1]-Vector((0,0,0.002))
    return out
for p in [(-197.5,-229.5),(-197.2,-229.8),(-197.8,-229.2),(-196.8,-230.5),(-198,-230.3),(-205,-230.5),(-210,-230.5),(-200,-230.8),(-183,-235),(-178,-248),(-176,-253),(-172,-254),(-180,-250)]:
    print(p,ray(*p))

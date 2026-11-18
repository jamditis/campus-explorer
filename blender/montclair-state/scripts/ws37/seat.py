# ws37: terrain poked through WS27 College Ave carriageway (green stripes in front of Kasser steps). Seat terrain under the carriageway along its whole length.
import bpy,bmesh,os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
Co=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; ce=Co.evaluated_get(dg); ci=Co.matrix_world.inverted()
def cz(x,y):
    ok,hp,_,_=ce.ray_cast(ci@Vector((x,y,400)),(ci.to_3x3()@Vector((0,0,-1))).normalized())
    return (Co.matrix_world@hp).z if ok else None
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
bb=[Co.matrix_world@Vector(c) for c in Co.bound_box]
x0,x1=min(p.x for p in bb)-1,max(p.x for p in bb)+1; y0,y1=min(p.y for p in bb)-1,max(p.y for p in bb)+1
print('bbox',round(x0,1),round(x1,1),round(y0,1),round(y1,1))
tm=T.matrix_world; ti=tm.inverted(); full=edge=0; maxd=0
for v in T.data.vertices:
    p=tm@v.co
    if not(x0<p.x<x1 and y0<p.y<y1): continue
    c=cz(p.x,p.y)
    zs=[cz(p.x+dx,p.y+dy) for dx,dy in ((0.6,0),(-0.6,0),(0,0.6),(0,-0.6))]
    ok=[z for z in zs if z is not None]
    if c is None:
        # vertex just outside but neighbours on road: ensure it doesn't rise above road edge
        if ok and len(ok)>=1:
            lim=min(ok)-0.02
            if p.z>lim: maxd=max(maxd,p.z-lim); v.co=ti@Vector((p.x,p.y,lim)); edge+=1
        continue
    lim=min([c]+ok)-(0.06 if len(ok)==4 else 0.03)
    if p.z>lim:
        maxd=max(maxd,p.z-lim); v.co=ti@Vector((p.x,p.y,lim)); full+=1
T.data.update(); print('seated full',full,'edge',edge,'max drop',round(maxd,3))
for o in list(bpy.data.objects):
    if o.type!='MESH' or not any(k in o.name.lower() for k in ('grass','lawn')): continue
    m=o.matrix_world; ob=[m@Vector(c) for c in o.bound_box]
    if max(q.x for q in ob)<x0 or min(q.x for q in ob)>x1 or max(q.y for q in ob)<y0 or min(q.y for q in ob)>y1: continue
    if len(o.data.polygons)>0 and len(o.data.vertices)>200000: continue
    b=bmesh.new(); b.from_mesh(o.data); kill=[]
    for vv in b.verts:
        p=m@vv.co
        if not(x0<p.x<x1 and y0<p.y<y1): continue
        z=cz(p.x,p.y)
        if z is not None and abs(z-p.z)<0.6: kill.append(vv)
    if kill:
        bmesh.ops.delete(b,geom=kill,context='VERTS'); b.to_mesh(o.data); o.data.update(); print('grass removed',o.name,len(kill))
    b.free()
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')

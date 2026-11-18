import bpy, numpy as np, time
from mathutils import Vector
t=time.time()
sc=bpy.context.scene
X0,X1,Y0,Y1=-88,-64,-224,-194
for o in sc.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if (max(xs)-min(xs))>400: tag='BIG'
    else: tag=''
    print('OBJ',o.name,tag,round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2),[m.name for m in o.data.materials if m][:4])
dg=bpy.context.evaluated_depsgraph_get()
print('dg',time.time()-t)
def rc(o,d):
    h=sc.ray_cast(dg,Vector(o),Vector(d))
    if not h[0]: return None
    ob=h[4]; mn='?'
    try:
        if ob.type=='MESH' and h[3]<len(ob.data.polygons): mn=ob.data.materials[ob.data.polygons[h[3]].material_index].name
    except Exception: pass
    return ob.name[:30],mn[:22],round(h[1].z,2)
for y in np.arange(-197,-222,-1.0):
    for x in np.arange(-84,-66,1.0):
        r=rc((x+.5,y-.5,200),(0,0,-1)); print('G',x+.5,y-.5,r)
print('DONE',time.time()-t)

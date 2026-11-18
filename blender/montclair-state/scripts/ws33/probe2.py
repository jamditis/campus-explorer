import bpy
from mathutils import Vector
c=bpy.data.objects['Curbs_granite_OSM']
md=c.modifiers['CurbSweep']; ng=md.node_group
print('ng',ng.name)
for it in ng.interface.items_tree:
    if getattr(it,'in_out',None)=='INPUT': print(' in',it.name,it.identifier, md.get(it.identifier))
for n in ng.nodes:
    vals=[(i.name,round(i.default_value,3) if isinstance(getattr(i,'default_value',None),float) else None) for i in n.inputs if not i.is_linked and hasattr(i,'default_value') and isinstance(i.default_value,float)]
    print(' node',n.bl_idname,n.name,vals[:6])
dg=bpy.context.evaluated_depsgraph_get()
def rz(o,x,y):
    e=o.evaluated_get(dg); mi=o.matrix_world.inverted()
    ok,hp,_,_=e.ray_cast(mi@Vector((x,y,200)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return round((o.matrix_world@hp).z,2) if ok else None
R=bpy.data.objects['Roads_OSM'];T=bpy.data.objects['Terrain_LiDAR_DTM_1m'];A=bpy.data.objects['CCOM_dock_apron_20261014jf3']
m=c.matrix_world
for si in (1,2):
    sp=c.data.splines[si]
    for p in sp.points:
        w=m@Vector(p.co[:3])
        if -12<w.x<10 and -62<w.y<-14:
            ce=rz(c,w.x,w.y)
            print(si,round(w.x,2),round(w.y,2),'pt',round(w.z,2),'curbtop',ce,'road+-1m',rz(R,w.x+1,w.y),rz(R,w.x-1,w.y),'terr+-1',rz(T,w.x+1,w.y),rz(T,w.x-1,w.y),'apr',rz(A,w.x+1.5,w.y))

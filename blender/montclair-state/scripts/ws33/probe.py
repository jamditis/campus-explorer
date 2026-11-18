import bpy
from mathutils import Vector
c=bpy.data.objects['Curbs_granite_OSM']
print('type',c.type,'mods',[(m.type,m.name) for m in c.modifiers])
d=c.data
if c.type=='CURVE':
    print('bevel',d.bevel_mode,d.bevel_depth,d.bevel_resolution,'obj',d.bevel_object,'extrude',d.extrude,'offset',d.offset,'fill',d.fill_mode,'twist',d.twist_mode,'mat',[m.name for m in d.materials])
    print('nsplines',len(d.splines))
    m=c.matrix_world
    for i,sp in enumerate(d.splines):
        pts=[m@Vector(p.co[:3]) for p in sp.points] if sp.type!='BEZIER' else [m@p.co for p in sp.bezier_points]
        near=[p for p in pts if -12<p.x<10 and -62<p.y<-14]
        if near: print(i,sp.type,len(pts),'near',len(near),[tuple(round(x,2) for x in p) for p in near[:6]], 'radius',[round(p.radius,2) for p in sp.points][:4] if sp.type!='BEZIER' else '')
for o in bpy.data.objects:
    if 'curb' in o.name.lower(): print('OBJ',o.name,o.type,round(o.location.x),round(o.location.y))

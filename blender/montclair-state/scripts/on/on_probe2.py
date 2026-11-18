import bpy, mathutils
from mathutils import Vector
P=Vector((-15.7,117.3))
c=[]
for o in bpy.data.objects:
    if o.name.startswith('SCH_win_'):
        t=o.matrix_world.translation
        d=(Vector((t.x,t.y))-P).length
        if d<6: c.append((d,o.name,tuple(round(v,2) for v in t),round(o.matrix_world.to_euler().z,3),o.hide_render,o.instance_type, o.instance_collection.name if o.instance_collection else '', tuple(round(s,2) for s in o.scale)))
for x in sorted(c): print('W',x)
# wall edges near P: vertical faces of Schmitt Hall walls
w=bpy.data.objects['Schmitt Hall walls']; me=w.data; M=w.matrix_world
for f in me.polygons:
    cc=M@f.center
    if abs(f.normal.z)<0.1 and (Vector((cc.x,cc.y))-P).length<5:
        vs=[M@me.vertices[i].co for i in f.vertices]
        xs=[(round(v.x,2),round(v.y,2)) for v in vs]
        print('F',f.index,tuple(round(n,2) for n in (M.to_3x3()@f.normal).normalized()), round(f.area,2), sorted(set(xs))[:6], round(min(v.z for v in vs),1), round(max(v.z for v in vs),1))

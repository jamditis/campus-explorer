import bpy
from mathutils import Vector
def bbox(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(c.x for c in bb),max(c.x for c in bb),min(c.y for c in bb),max(c.y for c in bb),min(c.z for c in bb),max(c.z for c in bb)
def inter(b,B): return not(b[1]<B[0] or b[0]>B[1] or b[3]<B[2] or b[2]>B[3])
print('== trees/instances near lot strip')
for o in bpy.data.objects:
    if o.type=='EMPTY' and o.instance_collection or 'tree' in o.name.lower():
        x,y=o.location.x,o.location.y
        if -185<x<-80 and -310<y<-255: print('T',o.name,o.type,round(x,1),round(y,1),round(o.location.z,1),tuple(round(s,2) for s in o.scale), o.instance_collection.name if o.instance_collection else '', [c.name for c in o.users_collection][:1])
print('== tree instance examples anywhere')
seen=set()
for o in bpy.data.objects:
    if o.type=='EMPTY' and o.instance_collection and 'Tree' in o.instance_collection.name and o.instance_collection.name not in seen:
        seen.add(o.instance_collection.name); print('E',o.name,o.instance_collection.name,o.instance_collection.library.filepath if o.instance_collection.library else 'local',tuple(round(s,2) for s in o.scale))
print('== lib collections');
for l in bpy.data.libraries: print('L',l.filepath)
for c in bpy.data.collections:
    if 'Tree' in c.name: print('C',c.name,c.library.filepath if c.library else 'local')
print('== meshes in wedge box x-172..-160 y-285..-262')
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    b=bbox(o)
    if inter(b,(-172,-160,-285,-262)) and (b[1]-b[0])<400:
        print('W',o.name,[m.name for m in o.data.materials][:3],len(o.data.polygons),tuple(round(v,1) for v in b))
print('== meshes near walk N end x-74..-68 y-204..-198')
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    b=bbox(o)
    if inter(b,(-74,-68,-204,-198)) and (b[1]-b[0])<600:
        print('N',o.name,[m.name for m in o.data.materials][:3],len(o.data.polygons),tuple(round(v,1) for v in b), [m.type for m in o.modifiers])

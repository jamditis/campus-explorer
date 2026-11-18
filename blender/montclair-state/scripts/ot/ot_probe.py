import bpy
from mathutils import Vector
from collections import defaultdict
c=bpy.data.collections['OR_skirt_base_course_20261031or']
for ob in c.objects:
    me=ob.data; mw=ob.matrix_world
    print('BC',ob.name,len(me.vertices),len(me.polygons),[a.name for a in me.attributes][:12])
    # group verts by xy (0.05 m) and report z spread of coincident columns between different polygon islands
    g=defaultdict(list)
    for v in me.vertices:
        w=mw@v.co; g[(round(w.x,1),round(w.y,1))].append(round(w.z,3))
    multi=[(k,sorted(z)) for k,z in g.items() if len(z)>2]
    print(' cols>2',len(multi), multi[:6])
# Calcia canopy candidates
cal=bpy.data.objects.get('Calcia Hall walls')
print('CAL', cal and [round(x,1) for x in cal.matrix_world.translation], cal and cal.data.materials[:] and [m.name for m in cal.data.materials])
import mathutils
bb=[cal.matrix_world@Vector(b) for b in cal.bound_box]
mn=Vector((min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb))); mx=Vector((max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb)))
print('CALBB',[round(x,1) for x in mn],[round(x,1) for x in mx])
for o in bpy.context.scene.objects:
    if o.type!='MESH' and o.type!='LIGHT': continue
    t=o.matrix_world.translation
    if mn.x-8<t.x<mx.x+8 and mn.y-8<t.y<mx.y+8 and ('anop' in o.name.lower() or 'calcia' in o.name.lower() or o.type=='LIGHT'):
        print('NEAR',o.type,o.name,[round(x,1) for x in t],[m.name for m in o.data.materials] if o.type=='MESH' else o.data.energy)
cam=bpy.data.objects.get('OQ_CAM_eye_calcia_skirt_windows'); print('CAM',[round(x,1) for x in cam.matrix_world.translation], [round(x,2) for x in cam.rotation_euler])
w=bpy.context.scene.world; print('WORLD',w.name,[n.type for n in w.node_tree.nodes])
print('SUN',[(o.name,o.data.energy,[round(x,2) for x in o.rotation_euler]) for o in bpy.context.scene.objects if o.type=='LIGHT' and o.data.type=='SUN'])

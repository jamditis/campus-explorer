import bpy, math
from mathutils import Vector
X0,X1,Y0,Y1=-318,-296,-250,-228
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    me=o.data
    mats=[m.name for m in me.materials if m]
    print('OBJ',o.name,'v',len(me.vertices),'f',len(me.polygons),'hr',o.hide_render,'mods',[(m.type,m.name) for m in o.modifiers],'mats',mats[:3],'z',round(min(v.z for v in bb),2),round(max(v.z for v in bb),2),flush=True)
d=[o for o in bpy.data.objects if o.name.startswith('WS163_Lot3_aisle_S_drive')][0]
M=d.matrix_world; me=d.data
# normal deviation stats
import collections
devs=[]
for p in me.polygons:
    n=(M.to_3x3()@p.normal).normalized(); devs.append((math.degrees(math.acos(max(-1,min(1,n.z)))),(M@p.center)))
devs.sort(key=lambda t:-t[0])
print('DRIVE faces',len(devs),'smooth',sum(p.use_smooth for p in me.polygons))
for a,c in devs[:25]: print('TILT %.1f'%a, round(c.x,2),round(c.y,2),round(c.z,2))
# adjacent-face normal jumps
import bmesh
bm=bmesh.new(); bm.from_mesh(me); bm.transform(M)
j=[]
for e in bm.edges:
    if len(e.link_faces)==2:
        a=math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal)); 
        if a>4: c=(e.verts[0].co+e.verts[1].co)/2; j.append((a,c))
j.sort(key=lambda t:-t[0]); print('CREASES>4deg',len(j))
for a,c in j[:30]: print('CR %.1f'%a,round(c.x,2),round(c.y,2),round(c.z,2))

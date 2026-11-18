import bpy, mathutils
A,B=-22.930214,0.238365
o=bpy.data.objects['School of Communication and Media walls']; me=o.data
print('LIB',o.library, me.library, me.users, len(me.polygons), o.matrix_world==mathutils.Matrix.Identity(4), [m.name for m in me.materials], [m.name for m in o.modifiers])
W=o.matrix_world
for p in me.polygons:
    vs=[W@me.vertices[i].co for i in p.vertices]
    ys=[v.y for v in vs]; zs=[v.z for v in vs]; xs=[v.x for v in vs]
    if max(ys)<9.0 or min(ys)>14.6 or max(zs)<137.5 or min(zs)>146.3: continue
    if max(abs(v.x-(A+B*v.y)) for v in vs)>0.3: continue
    print('F',p.index,len(vs),round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2),tuple(round(c,2) for c in p.normal))

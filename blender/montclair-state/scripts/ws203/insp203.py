import bpy, bmesh, numpy as np
from mathutils import Vector
X0,X1,Y0,Y1=-310,-294,-241,-232
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if o.name.startswith(('Context_skirt','BD_farfield')): continue
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    be=[e for e in bm.edges if e.is_boundary]
    seg=[]
    for e in be:
        a=mw@e.verts[0].co; b=mw@e.verts[1].co
        if X0<a.x<X1 and Y0<a.y<Y1: seg.append((round(a.x,2),round(a.y,2),round(a.z,3),round(b.x,2),round(b.y,2),round(b.z,3)))
    print('I203',o.name[:40],'hide_r',o.hide_render,'nv',len(o.data.vertices),'bnd_in_box',len(seg),'zr',round(min(v.z for v in bb),2),round(max(v.z for v in bb),2),[m.type for m in o.modifiers][:4],flush=True)
    if 0<len(seg)<400 and not o.name.startswith('Terrain'):
        np.save('/workspace/nj-scenes/montclair-state/scripts/ws203/bnd_%s.npy'%o.name[:20].replace(' ','_'),np.array(seg))
    bm.free()

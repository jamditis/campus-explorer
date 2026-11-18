import bpy
o=bpy.data.objects['Freeman Hall walls']; me=o.data; mw=o.matrix_world
print('FM mats',[m.name if m else None for m in me.materials],'verts',len(me.vertices),'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'scale',tuple(o.scale), 'users',me.users, me.name)
for p in me.polygons:
    vs=[mw@me.vertices[i].co for i in p.vertices]
    print('FP',p.index,len(vs),'mi',p.material_index,'n',tuple(round(c,2) for c in p.normal),'x',round(min(v.x for v in vs),1),round(max(v.x for v in vs),1),'y',round(min(v.y for v in vs),1),round(max(v.y for v in vs),1),'z',round(min(v.z for v in vs),1),round(max(v.z for v in vs),1))
import bmesh
bm=bmesh.new(); bm.from_mesh(me)
print('FM nonmanifold edges',sum(1 for e in bm.edges if not e.is_manifold),'boundary',sum(1 for e in bm.edges if e.is_boundary))
for e in bm.edges:
    if e.is_boundary: print('BE',[tuple(round(c,1) for c in (mw@v.co)) for v in e.verts])

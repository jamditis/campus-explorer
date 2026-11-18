import bpy,bmesh
o=bpy.data.objects['QG_north_strip_LiDAR_terrain_patch']
print('OBJ',len(o.data.vertices),len(o.data.polygons),[m.type for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots], o.hide_render, o.display_type)
M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(M)
print('BOUNDS',[round(min(v.co[i] for v in bm.verts),1) for i in range(3)],[round(max(v.co[i] for v in bm.verts),1) for i in range(3)])
inb=lambda c:-5<=c.x<60 and 95<=c.y<130
fc=[f for f in bm.faces if inb(f.calc_center_median())]
print('COURT faces',len(fc),'smooth',sum(f.smooth for f in fc), 'mean area',sum(f.calc_area() for f in fc)/max(1,len(fc)))
be=[e for e in bm.edges if e.is_boundary and inb((e.verts[0].co+e.verts[1].co)/2)]
print('COURT boundary edges',len(be))
import collections
nz=[f.normal.z for f in fc]; print('nz<0.9',sum(1 for z in nz if z<0.9),'nz<0.97',sum(1 for z in nz if z<0.97))
# boundary loops sizes
bm.edges.ensure_lookup_table()
seen=set();sizes=[]
for e in be:
    if e.index in seen: continue
    stack=[e];n=0
    while stack:
        x=stack.pop()
        if x.index in seen: continue
        seen.add(x.index);n+=1
        for v in x.verts:
            for y in v.link_edges:
                if y.is_boundary and y.index not in seen: stack.append(y)
    sizes.append(n)
print('LOOPS',len(sizes),sorted(sizes)[-10:],sum(1 for s in sizes if s<=12))
# z jumps: max dz between adjacent faces in court

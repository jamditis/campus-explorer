import bpy, json
from mathutils import Vector
for nm in ['SF_Lot38_stall_stripes','SF_Lot38_asphalt_313028558']:
    c=[o for o in bpy.data.objects if o.name.startswith(nm)]
    for o in c:
        me=o.data; M=o.matrix_world
        nz=[ (M.to_3x3()@p.normal).z for p in me.polygons]
        import collections
        h=collections.Counter(round(z,1) for z in nz)
        bb=[M@Vector(b) for b in o.bound_box]
        print('P220',o.name,o.type,'verts',len(me.vertices),'faces',len(me.polygons),'nz',dict(h),'mods',[(m.type,m.name) for m in o.modifiers],
              'mats',[s.material.name if s.material else None for s in o.material_slots],
              'bb',[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)],'parent',o.parent.name if o.parent else None, 'hide',o.hide_render, flush=True)
        if o.name.startswith('SF_Lot38_stall'):
            print('P220 scale',tuple(o.matrix_world.to_scale()),'det',o.matrix_world.determinant())
            for m in o.modifiers: print('P220 mod',m.type,{k:getattr(m,k) for k in dir(m) if k in ('thickness','offset','target','wrap_method','node_group')})
m=bpy.data.materials.get
for o in bpy.data.objects:
    if o.name.startswith('SF_Lot38_asphalt'):
        for s in o.material_slots:
            if s.material:
                users=[x.name[:40] for x in bpy.data.objects if x.type=='MESH' and any(t.material==s.material for t in x.material_slots)]
                print('P220 matusers',s.material.name,len(users),users[:8], [n.name for n in s.material.node_tree.nodes][:40])

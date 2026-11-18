import bpy, numpy as np
for n in ['QE_CCIS_drape_cover_wall_east_UNVERIFIED','QF_qe_cover_wall_windows_kept_red_UNVERIFIED','QH_CCIS_NE_junction_cover_UNVERIFIED']:
    o=bpy.data.objects.get(n)
    if not o: print('MISSING',n); continue
    me=o.data; v=np.array([o.matrix_world@x.co for x in me.vertices])
    print('OBJ',n,'type',o.type,'hide',o.hide_render,'verts',len(v),'faces',len(me.polygons),'mods',[m.name for m in o.modifiers],'mats',[m.name if m else None for m in me.materials])
    print('  min',v.min(0).round(2),'max',v.max(0).round(2))
    t=0.4*v[:,0]+0.92*v[:,1]; nn=0.92*v[:,0]-0.4*v[:,1]
    print('  t',t.min().round(2),t.max().round(2),'n',nn.min().round(2),nn.max().round(2))
    ns=np.array([tuple(o.matrix_world.to_3x3()@p.normal) for p in me.polygons])
    u,c=np.unique(ns.round(2),axis=0,return_counts=True); idx=np.argsort(-c)[:6]; print('  normals',[(tuple(u[i]),c[i]) for i in idx])
# CCIS east facade candidate objects near x 25..35, y 190..210
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if 'CCIS' in o.name or 'Computing' in o.name or 'QF_' in o.name[:3]:
        bb=np.array([o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]); print('C',o.name,bb.min(0).round(1),bb.max(0).round(1))

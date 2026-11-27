import bpy,os
F='/workspace/nj-scenes/montclair-state/'
with bpy.data.libraries.load(F+'montclair_state.blend') as (a,b): b.objects=[n for n in a.objects if n.startswith(('WS68_RHD_ground','M3b_north_LiDAR_DTM_1m_west','Red Hawk W core','fp_police_body','ge_police_terrace'))]
with bpy.data.libraries.load(F+'north/montclair_north.blend') as (a,c): c.objects=['ge_police_south_walk']
for o in list(b.objects)+list(c.objects):
    bb=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box]
    print('Q256',o.name[:50],'mods',[(m.name,m.type) for m in o.modifiers],'v',len(o.data.vertices) if o.type=='MESH' else '-','bbox x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f'%(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)),'cols',[cc.name for cc in o.users_collection],flush=True)
w=c.objects[0]; import collections
zs=collections.Counter(round(v.co.z,2) for v in w.data.vertices); print('Q256 walk polys',len(w.data.polygons),'up',sum(1 for p in w.data.polygons if p.normal.z>0.5),'down',sum(1 for p in w.data.polygons if p.normal.z<-0.5),flush=True)
os._exit(0)

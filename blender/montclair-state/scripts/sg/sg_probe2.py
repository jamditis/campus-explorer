import bpy,json,math
from mathutils import Vector, kdtree
dg=bpy.context.evaluated_depsgraph_get()
W=json.load(open('data/sf/north_lot_osm.json'))['ways']
road=W['313028548']['pts'][::-1]+W['313028549']['pts'][1:]
cands=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and ('oad' in o.name or 'Foot' in o.name or o.name.startswith(('QS_','QXP_','SB_','QX_')) ) and 'grass' not in o.name.lower()]
for o in cands:
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    pts=[mw@v.co for v in me.vertices]; e.to_mesh_clear()
    near={}
    for (x,y) in [(-83,369.6),(-80,366),(85,344),(100,337),(114.7,330.2),(130,323),(148.3,315.6)]:
        d=min((math.hypot(p.x-x,p.y-y) for p in pts),default=999)
        if d<6: near[(x,y)]=round(d,1)
    if near: print('NEAR',o.name,near)

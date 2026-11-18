import bpy, bmesh
from mathutils import Vector
print('PROBE start',flush=True)
for o in bpy.data.objects:
    if o.type!='MESH': continue
    n=o.name
    if any(n.startswith(p) for p in ('WS75','WS76','WS79','WS80','WS77')):
        me=o.data; xs=[v.co.x for v in me.vertices[:2000]]
        mw=o.matrix_world
        bb=[mw@Vector(c) for c in o.bound_box]
        print('OBJ',n,len(me.vertices),len(me.polygons),'mat',[m.name for m in me.materials if m][:3],'bb',round(min(b.x for b in bb),1),round(max(b.x for b in bb),1),round(min(b.y for b in bb),1),round(max(b.y for b in bb),1),'hide',o.hide_render,'mods',[m.type for m in o.modifiers],'ident',mw.is_identity if hasattr(mw,'is_identity') else None,flush=True)
        if len(me.vertices):
            v=me.vertices[0].co; w=mw@v; print('  v0',round(w.x,3),round(w.y,3),round(w.z,3),' frac',round(w.x%0.4,3),round(w.y%0.4,3))
# objects intersecting region x -233..-225, y -129..-111
R=(-233,-225,-129,-111)
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE') or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(b.x for b in bb),max(b.x for b in bb); y0,y1=min(b.y for b in bb),max(b.y for b in bb)
    if x1<R[0] or x0>R[1] or y1<R[2] or y0>R[3]: continue
    if (x1-x0)*(y1-y0)>5e5: big='BIG'
    else: big=''
    print('INREG',o.name,o.type,round(x0,1),round(x1,1),round(y0,1),round(y1,1),big,flush=True)
print('PROBE done',flush=True)

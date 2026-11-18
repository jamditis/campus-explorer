import bpy
from mathutils import Vector
@bpy.app.handlers.persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
for o in bpy.data.objects:
    if o.type!='MESH': continue
    M=o.matrix_world
    bb=[M@Vector(c) for c in o.bound_box]
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1<-275 or x0>-245 or y1<-56 or y0>-42: continue
    print('P217',o.name[:70],len(o.data.vertices),[m.name for m in o.data.materials if m][:3],round(x0,1),round(x1,1),round(y0,1),round(y1,1),flush=True)
AP=next(o for o in bpy.data.objects if o.name.startswith('KX_drive_apron'))
M=AP.matrix_world
for v in AP.data.vertices:
    w=M@v.co
    if -54<w.y<-44 and w.x>-275: print('APV',v.index,round(w.x,2),round(w.y,2),round(w.z,3))
print('APPOLYS',len(AP.data.polygons),'mods',[m.type for m in AP.modifiers])
